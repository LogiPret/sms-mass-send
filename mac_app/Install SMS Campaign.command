#!/bin/bash
# SMS Campaign - Mac Installer
# Double-click to install and run
# Automatically installs Python if needed

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
APP_NAME="SMS Campaign"
INSTALL_DIR="$HOME/.sms_campaign"
SCRIPT_URL="https://gist.githubusercontent.com/HugoOtth/3e89759cac04be452c935c90b5733eea/raw/sms_campaign.py"
SCRIPT_FILE="$INSTALL_DIR/sms_campaign.py"

clear
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║       SMS Campaign - Installation      ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""

# Create install directory
mkdir -p "$INSTALL_DIR"

# Function to check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Function to find Python 3
find_python() {
    if command_exists python3; then
        echo "python3"
    elif command_exists /usr/bin/python3; then
        echo "/usr/bin/python3"
    elif command_exists /usr/local/bin/python3; then
        echo "/usr/local/bin/python3"
    elif command_exists /opt/homebrew/bin/python3; then
        echo "/opt/homebrew/bin/python3"
    else
        echo ""
    fi
}

# Check for Python
PYTHON_CMD=$(find_python)

if [ -z "$PYTHON_CMD" ]; then
    echo -e "${YELLOW}⚠️  Python 3 non trouvé${NC}"
    echo ""
    
    # Check for Xcode Command Line Tools (includes Python on newer macOS)
    if ! xcode-select -p &> /dev/null; then
        echo -e "${BLUE}Installation des outils de développement macOS...${NC}"
        echo "Cela peut prendre quelques minutes."
        echo ""
        xcode-select --install
        
        echo ""
        echo -e "${YELLOW}Veuillez terminer l'installation dans la fenêtre qui s'est ouverte,${NC}"
        echo -e "${YELLOW}puis relancez ce script.${NC}"
        echo ""
        read -p "Appuyez sur Entrée pour quitter..."
        exit 0
    fi
    
    # Try again after Xcode tools
    PYTHON_CMD=$(find_python)
    
    if [ -z "$PYTHON_CMD" ]; then
        # Still no Python - suggest Homebrew
        echo -e "${YELLOW}Python 3 n'est toujours pas disponible.${NC}"
        echo ""
        
        if command_exists brew; then
            echo -e "${BLUE}Installation de Python via Homebrew...${NC}"
            brew install python3
            PYTHON_CMD=$(find_python)
        else
            echo "Options d'installation:"
            echo ""
            echo "1. Installer Homebrew + Python (recommandé):"
            echo -e "   ${BLUE}/bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"${NC}"
            echo "   brew install python3"
            echo ""
            echo "2. Télécharger Python depuis python.org:"
            echo -e "   ${BLUE}https://www.python.org/downloads/macos/${NC}"
            echo ""
            read -p "Voulez-vous installer Homebrew maintenant? (o/n): " INSTALL_BREW
            
            if [ "$INSTALL_BREW" = "o" ] || [ "$INSTALL_BREW" = "O" ]; then
                echo ""
                echo -e "${BLUE}Installation de Homebrew...${NC}"
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
                
                # Add Homebrew to PATH for Apple Silicon Macs
                if [ -f /opt/homebrew/bin/brew ]; then
                    eval "$(/opt/homebrew/bin/brew shellenv)"
                fi
                
                echo ""
                echo -e "${BLUE}Installation de Python...${NC}"
                brew install python3
                PYTHON_CMD=$(find_python)
            else
                echo ""
                echo -e "${RED}Installation annulée.${NC}"
                echo "Installez Python 3 manuellement puis relancez ce script."
                read -p "Appuyez sur Entrée pour quitter..."
                exit 1
            fi
        fi
    fi
fi

if [ -z "$PYTHON_CMD" ]; then
    echo -e "${RED}❌ Python 3 n'a pas pu être installé.${NC}"
    read -p "Appuyez sur Entrée pour quitter..."
    exit 1
fi

echo -e "${GREEN}✅ Python trouvé: $PYTHON_CMD${NC}"
$PYTHON_CMD --version
echo ""

# Download or update the script
echo -e "${BLUE}📥 Téléchargement de SMS Campaign...${NC}"
if curl -fsSL "$SCRIPT_URL" -o "$SCRIPT_FILE.tmp"; then
    # Check if download is valid
    if [ -s "$SCRIPT_FILE.tmp" ]; then
        mv "$SCRIPT_FILE.tmp" "$SCRIPT_FILE"
        echo -e "${GREEN}✅ Script téléchargé${NC}"
    else
        echo -e "${RED}❌ Téléchargement vide${NC}"
        rm -f "$SCRIPT_FILE.tmp"
        
        if [ -f "$SCRIPT_FILE" ]; then
            echo -e "${YELLOW}Utilisation de la version locale${NC}"
        else
            read -p "Appuyez sur Entrée pour quitter..."
            exit 1
        fi
    fi
else
    echo -e "${YELLOW}⚠️  Téléchargement échoué${NC}"
    
    if [ -f "$SCRIPT_FILE" ]; then
        echo -e "${YELLOW}Utilisation de la version locale${NC}"
    else
        echo -e "${RED}Aucune version disponible${NC}"
        read -p "Appuyez sur Entrée pour quitter..."
        exit 1
    fi
fi

echo ""
echo -e "${GREEN}🚀 Lancement de SMS Campaign...${NC}"
echo ""

# Run the app
cd "$INSTALL_DIR"
$PYTHON_CMD "$SCRIPT_FILE"

# Keep terminal open if there was an error
if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}L'application s'est terminée avec une erreur.${NC}"
    read -p "Appuyez sur Entrée pour quitter..."
fi
