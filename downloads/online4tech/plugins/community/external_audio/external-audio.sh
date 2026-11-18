#!/bin/bash

# ---------------------------
# external-audio Setup Script
# ---------------------------

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
RESET='\033[0m'

ARCH=""
PY_VER=""
TAR_GZ=""
PLUGIN_NAME="external_audio"
BASE_URL="https://github.com/emilnabil/download-plugins/raw/refs/heads/main/external_audio"

welcome_message() {
    echo -e "${CYAN}##########################################${RESET}"
    echo -e "${YELLOW}###    Welcome to external-audio Setup!    ###${RESET}"
    echo -e "${CYAN}##########################################${RESET}"
}

detect_python_version() {
    if command -v python3 &>/dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        PYTHON_VERSION=$(echo "$PYTHON_VERSION" | cut -d'.' -f1-2)
        echo "$PYTHON_VERSION"
    elif command -v python &>/dev/null; then
        PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
        PYTHON_VERSION=$(echo "$PYTHON_VERSION" | cut -d'.' -f1-2)
        echo "$PYTHON_VERSION"
    else
        echo -e "${RED}Python is not installed. Please install Python.${RESET}"
        exit 1
    fi
}

install_ffmpeg() {
    echo -e "${YELLOW}Installing ffmpeg...${RESET}"
    opkg update && opkg install ffmpeg
    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}ffmpeg installed successfully!${RESET}"
    else
        echo -e "${RED}Failed to install ffmpeg${RESET}"
    fi
}

detect_cpu_arch() {
    echo "Checking Python version..."
    PY_VER=$(detect_python_version)
    echo "Python version: $PY_VER"

    echo "Detecting CPU architecture..."
    CPU_ARCH=$(uname -m)
    echo -e "CPU architecture: ${GREEN}${CPU_ARCH}${RESET}"

    if [[ "$CPU_ARCH" == *"arm"* ]]; then
        ARCH=$(detect_arm_arch)
        if [[ "$ARCH" != "unknown" ]]; then
            TAR_GZ="adp_${ARCH}_py${PY_VER}.tar.gz"
            echo -e "Detected architecture: ${GREEN}${ARCH}${RESET}"
        else
            echo -e "${RED}Unsupported ARM architecture${RESET}"
            exit 1
        fi
    elif [[ "$CPU_ARCH" == *"mips"* ]]; then
        ARCH="mips32el"
        TAR_GZ="adp_mips32el_py${PY_VER}.tar.gz"
        echo "Detected architecture: mipsel"
    elif [[ "$CPU_ARCH" == *"aarch64"* ]]; then
        ARCH="aarch64"
        TAR_GZ="adp_aarch64_py${PY_VER}.tar.gz"
        echo "Detected architecture: aarch64"
    else
        echo -e "${RED}Unsupported architecture: ${CPU_ARCH}${RESET}"
        exit 1
    fi
}

detect_arm_arch() {
    OPKG_DIR="/etc/opkg/"
    if [[ -d "$OPKG_DIR" ]]; then
        if ls "$OPKG_DIR" 2>/dev/null | grep -q "cortexa15hf-neon-vfpv4"; then
            echo "cortexa15hf-neon-vfpv4"
        elif ls "$OPKG_DIR" 2>/dev/null | grep -q "cortexa9hf-neon"; then
            echo "cortexa9hf-neon"
        elif ls "$OPKG_DIR" 2>/dev/null | grep -q "cortexa7hf-vfp"; then
            echo "cortexa7hf-vfp"
        elif ls "$OPKG_DIR" 2>/dev/null | grep -q "armv7ahf-neon"; then
            echo "armv7ahf-neon"
        else
            echo "unknown"
        fi
    else
        echo "unknown"
    fi
}

download_plugin() {
    if [[ -z "$TAR_GZ" ]]; then
        echo -e "${RED}Error: No package file specified${RESET}"
        exit 1
    fi
    
    DOWNLOAD_URL="${BASE_URL}/${TAR_GZ}"
    echo -e "${YELLOW}Downloading from: ${DOWNLOAD_URL}${RESET}"
    
    wget -q --show-progress "$DOWNLOAD_URL" -O "/tmp/$TAR_GZ"
    
    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}Download successful!${RESET}"
        return 0
    else
        echo -e "${RED}Download failed!${RESET}"
        return 1
    fi
}

extract_and_install() {
    echo -e "${YELLOW}Extracting and installing plugin...${RESET}"
    
    if [[ ! -f "/tmp/$TAR_GZ" ]]; then
        echo -e "${RED}Package file not found: /tmp/$TAR_GZ${RESET}"
        return 1
    fi
    
    # استخراج الملف مباشرة إلى المسار الجذر /
    echo -e "${YELLOW}Extracting to root directory...${RESET}"
    tar -xzf "/tmp/$TAR_GZ" -C /
    
    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}Extraction successful!${RESET}"
        
        # حذف الملف المؤقت
        rm -f "/tmp/$TAR_GZ"
        
        echo -e "${GREEN}Plugin installed successfully!${RESET}"
        return 0
    else
        echo -e "${RED}Extraction failed!${RESET}"
        return 1
    fi
}

download_config_file() {
    echo -e "${YELLOW}Downloading configuration file...${RESET}"
    
    # إنشاء المجلد إذا لم يكن موجوداً
    mkdir -p /etc/enigma2
    
    wget -q --show-progress -O /etc/enigma2/external_audio.txt "${BASE_URL}/external_audio.txt"
    
    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}Configuration file downloaded successfully!${RESET}"
        return 0
    else
        echo -e "${RED}Failed to download configuration file${RESET}"
        return 1
    fi
}

restart_box() {
    echo -e "${YELLOW}Restarting Enigma2...${RESET}"
    sleep 2
    killall -9 enigma2
    exit 0
}

install_plugin() {
    welcome_message
    detect_cpu_arch
    install_ffmpeg
    
    if download_plugin; then
        if extract_and_install; then
            download_config_file
            restart_box
        else
            echo -e "${RED}Installation failed. Please try again.${RESET}"
            exit 1
        fi
    else
        echo -e "${RED}Download failed. Please check your internet connection and try again.${RESET}"
        exit 1
    fi
}

# Main execution
install_plugin

