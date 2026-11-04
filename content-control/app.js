import { createClient } from "https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.102.0/+esm";

const SUPABASE_URL = "https://vsdhqzgxhxjbntmhxfdk.supabase.co";
const SUPABASE_PUBLISHABLE_KEY = "sb_publishable_lsoBbrZ0omHuyP_LYikVbQ_-uoN3Bga";
const supabase = createClient(SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY);

const $ = (id) => document.getElementById(id);
const views = ["authView", "passwordView", "dashboardView"];
let currentUser = null;
let plans = [];
let posts = [];

function showView(id) {
  views.forEach((view) => $(view).hidden = view !== id);
  $("signOutBtn").hidden = id !== "dashboardView";
}
function setMessage(id, message, type = "") {
  const el = $(id);
  el.textContent = message || "";
  el.className = "message" + (type ? " " + type : "");
}
function formatDate(value) {
  if (!value) return "بدون موعد محدد";
  return new Intl.DateTimeFormat("ar-EG", { dateStyle: "medium" }).format(new Date(value + (String(value).length === 10 ? "T00:00:00" : "")));
}
function statusLabel(status) {
  return ({ draft:"مسودة", review:"بانتظار المراجعة", approved:"معتمد", scheduled:"مجدول يدويًا", published:"تم النشر", failed:"تعذّر النشر" })[status] || status;
}
function safeText(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({ "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;" })[char]);
}
function authFlowType() {
  return new URLSearchParams(location.hash.slice(1)).get("type");
}

async function handleSession(session) {
  currentUser = session?.user || null;
  if (!currentUser) {
    showView("authView");
    return;
  }
  const flow = authFlowType();
  if (flow === "invite" || flow === "recovery") {
    showView("passwordView");
    return;
  }
  const { data, error } = await supabase.from("content_admins").select("role").eq("user_id", currentUser.id).maybeSingle();
  if (error || !data || data.role !== "admin") {
    await supabase.auth.signOut();
    currentUser = null;
    showView("authView");
    setMessage("authMessage", "الحساب مسجّل، لكنه غير مصرح له بدخول لوحة الإدارة. راجع صلاحية المدير.", "error");
    return;
  }
  history.replaceState(null, "", location.pathname + location.search);
  showView("dashboardView");
  $("dashboardMessage").textContent = "";
  await loadDashboard();
}

$("loginForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  setMessage("authMessage", "جاري التحقق من بيانات الدخول...");
  const email = $("loginEmail").value.trim();
  const password = $("loginPassword").value;
  const { data, error } = await supabase.auth.signInWithPassword({ email, password });
  if (error) return setMessage("authMessage", "تعذّر تسجيل الدخول. راجع البريد وكلمة المرور أو استخدم إعادة تعيين كلمة المرور.", "error");
  await handleSession(data.session);
});
$("forgotBtn").addEventListener("click", async () => {
  const email = $("loginEmail").value.trim();
  if (!email) return setMessage("authMessage", "اكتب بريد حساب المدير أولًا.", "error");
  setMessage("authMessage", "جاري إرسال رابط إعادة تعيين كلمة المرور...");
  const redirectTo = location.origin + location.pathname;
  const { error } = await supabase.auth.resetPasswordForEmail(email, { redirectTo });
  setMessage("authMessage", error ? "تعذّر إرسال الرابط. تأكد من إعداد رابط الموقع المسموح في Supabase." : "لو البريد مسجل، هيوصلك رابط إعادة تعيين. افتحه من نفس المتصفح.", error ? "error" : "success");
});
$("passwordForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const password = $("newPassword").value;
  if (password.length < 10) return setMessage("passwordMessage", "استخدم 10 أحرف على الأقل.", "error");
  if (password !== $("confirmPassword").value) return setMessage("passwordMessage", "كلمتا المرور غير متطابقتين.", "error");
  setMessage("passwordMessage", "جاري حفظ كلمة المرور...");
  const { error } = await supabase.auth.updateUser({ password });
  if (error) return setMessage("passwordMessage", "تعذّر حفظ كلمة المرور. افتح رابط الدعوة أو الاستعادة مرة أخرى.", "error");
  history.replaceState(null, "", location.pathname + location.search);
  setMessage("passwordMessage", "تم حفظ كلمة المرور. جاري فتح لوحة الإدارة...", "success");
  await handleSession((await supabase.auth.getSession()).data.session);
});
$("signOutBtn").addEventListener("click", async () => {
  await supabase.auth.signOut();
  currentUser = null;
  showView("authView");
  setMessage("authMessage", "تم تسجيل الخروج.", "success");
});

async function loadDashboard() {
  const [plansResult, postsResult] = await Promise.all([
    supabase.from("weekly_plans").select("id,week_start,title,status,created_at").order("week_start", { ascending:false }),
    supabase.from("content_posts").select("id,plan_id,sort_order,platforms,post_type,title,body,media_url,scheduled_at,publish_mode,status,approved_at,created_at").order("created_at", { ascending:false })
  ]);
  if (plansResult.error || postsResult.error) {
    setMessage("dashboardMessage", "حصلت مشكلة في تحميل البيانات. راجع إعداد Data API وصلاحيات الجداول في Supabase.", "error");
    return;
  }
  plans = plansResult.data || [];
  posts = postsResult.data || [];
  renderPlans();
  renderPosts();
  $("plansCount").textContent = plans.length;
  $("postsCount").textContent = posts.length;
  $("reviewCount").textContent = posts.filter(p => p.status === "draft" || p.status === "review").length;
  $("approvedCount").textContent = posts.filter(p => p.status === "approved").length;
}

function renderPlans() {
  $("plansList").innerHTML = plans.length ? plans.map(plan => `
    <div class="plan-item"><div><strong>${safeText(plan.title)}</strong><small>${formatDate(plan.week_start)} · ${safeText(plan.status)}</small></div><span class="tag">${posts.filter(p=>p.plan_id===plan.id).length} منشور</span></div>`).join("") : '<div class="empty">لسه مفيش خطط. ابدأ بإنشاء أول خطة أسبوعية.</div>';
  $("postPlan").innerHTML = '<option value="">اختار الخطة</option>' + plans.map(p => `<option value="${p.id}">${safeText(p.title)} — ${formatDate(p.week_start)}</option>`).join("");
  const oldFilter = $("planFilter").value;
  $("planFilter").innerHTML = '<option value="all">كل الخطط</option>' + plans.map(p => `<option value="${p.id}">${safeText(p.title)}</option>`).join("");
  $("planFilter").value = plans.some(p=>p.id===oldFilter) ? oldFilter : "all";
}

function renderPosts() {
  const filter = $("planFilter").value;
  const visible = posts.filter(p => filter === "all" || p.plan_id === filter);
  $("postsList").innerHTML = visible.length ? visible.map(post => {
    const plan = plans.find(p=>p.id===post.plan_id);
    const canApprove = post.status === "draft" || post.status === "review";
    return `<article class="post-card">
      <div class="post-top"><h3>${safeText(post.title)}</h3><span class="status ${safeText(post.status)}">${statusLabel(post.status)}</span></div>
      <div class="post-meta"><span class="tag">${post.post_type==="reel"?"ريل":post.post_type==="story"?"ستوري":"منشور"}</span><span class="tag">${safeText((post.platforms||[]).join(" · "))}</span><span class="tag">${safeText(plan?.title || "خطة غير معروفة")}</span></div>
      <p class="post-body">${safeText(post.body)}</p>
      <div class="post-meta"><span>موعد مقترح: ${post.scheduled_at ? new Date(post.scheduled_at).toLocaleString("ar-EG") : "غير محدد"}</span><span>طريقة النشر: يدوي</span></div>
      ${post.media_url ? `<a href="${safeText(post.media_url)}" target="_blank" rel="noopener noreferrer">فتح رابط الوسائط</a>` : ""}
      <div class="post-actions">${post.status !== "published" && post.status !== "scheduled" ? `<button class="button ghost edit-btn" data-id="${post.id}" type="button">تعديل</button>` : ""}${canApprove ? `<button class="button primary approve-btn" data-id="${post.id}" type="button">اعتماد المحتوى</button>` : ""}</div>
    </article>`;
  }).join("") : '<div class="empty">مفيش منشورات في التصنيف ده حاليًا.</div>';
  document.querySelectorAll(".approve-btn").forEach(btn => btn.addEventListener("click", () => approvePost(btn.dataset.id))); 
  document.querySelectorAll(".edit-btn").forEach(btn => btn.addEventListener("click", () => startEditPost(btn.dataset.id)));
}

async function approvePost(id) {
  const post = posts.find(p=>p.id===id);
  if (!post || !["draft","review"].includes(post.status)) return;
  if (!confirm("تأكيد اعتماد هذا المنشور؟ الاعتماد لا ينشره ولا يرسله إلى Metricool.")) return;
  const { error } = await supabase.from("content_posts").update({ status:"approved", approved_at:new Date().toISOString() }).eq("id", id);
  if (error) return setMessage("dashboardMessage", "تعذّر اعتماد المنشور. حاول مرة أخرى.", "error");
  setMessage("dashboardMessage", "تم اعتماد المنشور. لم يتم نشره أو جدولته.", "success");
  await loadDashboard();
}

$("planForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const week_start = $("weekStart").value;
  const title = $("planTitle").value.trim();
  if (!week_start || !title) return;
  const { error } = await supabase.from("weekly_plans").insert({ week_start, title, status:"draft" });
  if (error) return setMessage("dashboardMessage", error.code === "23505" ? "فيه خطة مسجلة بالفعل لنفس تاريخ بداية الأسبوع." : "تعذّر حفظ الخطة.", "error");
  $("planForm").reset();
  $("planTitle").value = "خطة Online4Tech الأسبوعية";
  setMessage("dashboardMessage", "تم إنشاء الخطة الأسبوعية.", "success");
  await loadDashboard();
});

function resetPostEditor() {
  $("postForm").reset();
  $("postId").value = "";
  $("postSubmitBtn").textContent = "حفظ كمسودة";
  $("cancelPostEdit").hidden = true;
  document.querySelectorAll('input[name="platform"]').forEach(input => input.checked = ["facebook","instagram"].includes(input.value));
}
function startEditPost(id) {
  const post = posts.find(item => item.id === id);
  if (!post) return;
  $("postId").value = post.id;
  $("postPlan").value = post.plan_id;
  $("postTitle").value = post.title;
  $("postBody").value = post.body;
  $("postType").value = post.post_type;
  $("mediaUrl").value = post.media_url || "";
  $("scheduledAt").value = post.scheduled_at ? new Date(post.scheduled_at).toISOString().slice(0,16) : "";
  document.querySelectorAll('input[name="platform"]').forEach(input => input.checked = (post.platforms || []).includes(input.value));
  $("postSubmitBtn").textContent = "حفظ التعديلات";
  $("cancelPostEdit").hidden = false;
  $("postForm").scrollIntoView({ behavior:"smooth", block:"center" });
}
$("cancelPostEdit").addEventListener("click", resetPostEditor);
$("postForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const platforms = [...document.querySelectorAll('input[name="platform"]:checked')].map(input=>input.value);
  if (!platforms.length) return setMessage("dashboardMessage", "اختار منصة واحدة على الأقل.", "error");
  const plan_id = $("postPlan").value;
  if (!plan_id) return setMessage("dashboardMessage", "أنشئ أو اختار خطة أسبوعية أولًا.", "error");
  const scheduledValue = $("scheduledAt").value;
  const payload = {
    plan_id,
    title:$("postTitle").value.trim(),
    body:$("postBody").value.trim(),
    post_type:$("postType").value,
    platforms,
    media_url:$("mediaUrl").value.trim() || null,
    scheduled_at:scheduledValue ? new Date(scheduledValue).toISOString() : null,
    publish_mode:"manual"
  };
  const editId = $("postId").value;
  let error;
  if (editId) {
    const result = await supabase.from("content_posts").update({ ...payload, status:"draft", approved_at:null }).eq("id", editId);
    error = result.error;
  } else {
    const result = await supabase.from("content_posts").insert({ ...payload, status:"draft" });
    error = result.error;
  }
  if (error) return setMessage("dashboardMessage", "تعذّر حفظ المنشور. راجع البيانات وحاول تاني.", "error");
  resetPostEditor();
  setMessage("dashboardMessage", editId ? "تم حفظ التعديلات وإرجاع المنشور لمسودة للمراجعة من جديد." : "تم حفظ المنشور كمسودة للمراجعة.", "success");
  await loadDashboard();
});
$("planFilter").addEventListener("change", renderPosts);

supabase.auth.onAuthStateChange((_event, session) => {
  void handleSession(session);
});
const initialSession = await supabase.auth.getSession();
await handleSession(initialSession.data.session);
