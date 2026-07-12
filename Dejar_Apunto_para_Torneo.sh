#!/bin/bash

# =====================================================
# SCRIPT PARA PREPARAR KALI PARA TORNEOS CTF
# Versión: 1.0
# Autor: Tu asistente CTF
# Uso: sudo ./preparar_ctf.sh
# =====================================================

# Colores para la salida
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# =====================================================
# 1. MOSTRAR ESTADO INICIAL
# =====================================================
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   PREPARANDO KALI PARA CTF 🏆${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

echo -e "${YELLOW}[*] Estado inicial de la RAM:${NC}"
free -h
echo ""

# =====================================================
# 2. PREGUNTAR QUÉ HACER
# =====================================================
echo -e "${YELLOW}¿Qué quieres hacer?${NC}"
echo "1) Modo CTF completo (para torneos)"
echo "2) Modo ligero (solo terminal, sin GUI)"
echo "3) Solo limpieza rápida (libera RAM y caché)"
echo "4) Modo normal (deshacer cambios del modo CTF)"
echo "5) Salir"
echo ""
read -p "Elige una opción (1-5): " OPCION

# =====================================================
# 3. FUNCIONES
# =====================================================

# Función: Crear estructura de carpetas
crear_carpetas() {
    echo -e "${GREEN}[✓] Creando estructura de carpetas...${NC}"
    mkdir -p /home/kr3s4l4/TorneosCTF/CTF_$(date +%Y)/{web,forense,cripto,pwn,reversing,osint,exploits,payloads}
    mkdir -p /home/kr3s4l4/TorneosCTF/CTF_$(date +%Y)/tmp
    echo -e "${GREEN}[✓] Carpetas creadas en /home/kr3s4l4/TorneosCTF/CTF_$(date +%Y)${NC}"
}

# Función: Detener servicios innecesarios
detener_servicios() {
    echo -e "${GREEN}[✓] Deteniendo servicios innecesarios...${NC}"
    
    # Servicios de escritorio
    systemctl stop bluetooth 2>/dev/null
    systemctl stop cups 2>/dev/null
    systemctl stop avahi-daemon 2>/dev/null
    systemctl stop ModemManager 2>/dev/null
    systemctl stop accounts-daemon 2>/dev/null
    
    # Docker (si no lo usas)
    systemctl stop docker 2>/dev/null
    systemctl stop docker.socket 2>/dev/null
    systemctl stop containerd 2>/dev/null
    
    echo -e "${GREEN}[✓] Servicios detenidos${NC}"
}

# Función: Matar procesos pesados
matar_procesos() {
    echo -e "${GREEN}[✓] Matando procesos pesados...${NC}"
    
    # Navegadores
    pkill firefox 2>/dev/null
    pkill chrome 2>/dev/null
    pkill chromium 2>/dev/null
    
    # Escritorio
    pkill orca 2>/dev/null
    pkill speech-dispatcher 2>/dev/null
    pkill xfce4-screensaver 2>/dev/null
    pkill blueman-applet 2>/dev/null
    pkill system-config-printer 2>/dev/null
    
    # Herramientas que puedan estar abiertas
    pkill wireshark 2>/dev/null
    pkill burpsuite 2>/dev/null
    pkill ghidra 2>/dev/null
    
    echo -e "${GREEN}[✓] Procesos matados${NC}"
}

# Función: Liberar caché y memoria
liberar_memoria() {
    echo -e "${GREEN}[✓] Liberando caché y memoria...${NC}"
    
    # Sincronizar discos
    sync
    
    # Liberar caché de páginas, dentries e inodos
    echo 3 > /proc/sys/vm/drop_caches
    
    # Limpiar swap
    swapoff -a && swapon -a 2>/dev/null
    
    # Limpiar /tmp
    rm -rf /tmp/* 2>/dev/null
    
    # Limpiar caché de thumbnails
    rm -rf ~/.cache/thumbnails/* 2>/dev/null
    rm -rf /root/.cache/thumbnails/* 2>/dev/null
    
    # Limpiar caché de APT
    apt clean 2>/dev/null
    apt autoclean 2>/dev/null
    
    echo -e "${GREEN}[✓] Memoria liberada${NC}"
}

# Función: Configurar swappiness
configurar_swappiness() {
    echo -e "${GREEN}[✓] Configurando swappiness a 10...${NC}"
    echo 10 > /proc/sys/vm/swappiness
    echo "vm.swappiness=10" >> /etc/sysctl.conf 2>/dev/null
}

# Función: Modo completo (todo)
modo_completo() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}   ACTIVANDO MODO CTF COMPLETO${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    
    crear_carpetas
    detener_servicios
    matar_procesos
    liberar_memoria
    configurar_swappiness
    
    echo ""
    echo -e "${GREEN}✅ MODO CTF COMPLETO ACTIVADO${NC}"
    mostrar_estado
}

# Función: Modo ligero (solo terminal)
modo_ligero() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}   ACTIVANDO MODO LIGERO (TERMINAL)${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    
    echo -e "${YELLOW}[!] Este modo detendrá el entorno gráfico (lightdm)${NC}"
    echo -e "${YELLOW}[!] Para volver, ejecuta: systemctl start lightdm${NC}"
    read -p "¿Estás seguro? (s/n): " CONFIRMAR
    
    if [[ $CONFIRMAR == "s" || $CONFIRMAR == "S" ]]; then
        detener_servicios
        matar_procesos
        liberar_memoria
        configurar_swappiness
        
        # Detener GUI
        systemctl stop lightdm 2>/dev/null
        
        echo ""
        echo -e "${GREEN}✅ MODO LIGERO ACTIVADO (sin GUI)${NC}"
        echo -e "${YELLOW}[!] Para volver a la GUI: systemctl start lightdm${NC}"
    else
        echo -e "${RED}[!] Cancelado${NC}"
    fi
}

# Función: Limpieza rápida
limpieza_rapida() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}   LIMPIEZA RÁPIDA${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    
    matar_procesos
    liberar_memoria
    
    echo ""
    echo -e "${GREEN}✅ LIMPIEZA RÁPIDA COMPLETADA${NC}"
    mostrar_estado
}

# Función: Modo normal (deshacer cambios)
modo_normal() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}   RESTAURANDO MODO NORMAL${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    
    # Reactivar servicios
    systemctl start bluetooth 2>/dev/null
    systemctl start cups 2>/dev/null
    systemctl start avahi-daemon 2>/dev/null
    systemctl start ModemManager 2>/dev/null
    systemctl start accounts-daemon 2>/dev/null
    
    # Reactivar Docker
    systemctl start docker 2>/dev/null
    systemctl start containerd 2>/dev/null
    
    # Restaurar swappiness
    echo 60 > /proc/sys/vm/swappiness
    sed -i '/vm.swappiness=10/d' /etc/sysctl.conf 2>/dev/null
    
    # Reactivar GUI
    systemctl start lightdm 2>/dev/null
    
    echo -e "${GREEN}✅ MODO NORMAL RESTAURADO${NC}"
    mostrar_estado
}

# Función: Mostrar estado final
mostrar_estado() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}   ESTADO DEL SISTEMA${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    
    echo -e "${YELLOW}[*] RAM:${NC}"
    free -h
    echo ""
    
    echo -e "${YELLOW}[*] Procesos más pesados (top 5):${NC}"
    ps aux --sort=-%mem | head -6
    echo ""
    
    echo -e "${YELLOW}[*] Carga del sistema:${NC}"
    uptime
    echo ""
    
    echo -e "${YELLOW}[*] Servicios activos:${NC}"
    systemctl list-units --type=service --state=running | grep -E "(docker|bluetooth|cups|avahi|ModemManager)" | head -5
}

# =====================================================
# 4. EJECUTAR SEGÚN OPCIÓN
# =====================================================

case $OPCION in
    1)
        modo_completo
        ;;
    2)
        modo_ligero
        ;;
    3)
        limpieza_rapida
        ;;
    4)
        modo_normal
        ;;
    5)
        echo -e "${YELLOW}[!] Saliendo...${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}[!] Opción no válida${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}¡Listo! 🏆 Buena suerte en el torneo!${NC}"
