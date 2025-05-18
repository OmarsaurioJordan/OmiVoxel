# Creador de graficos 2.5D estilo Voxel, por Omarsaurio 2020

import numpy as np
import pygame as pg
from threading import Thread as th
from datetime import datetime as dt
from PIL import Image
import os

def preInicio(w, h):
    txt = input("digite w,h del lienzo, def ({},{}): ".format(w, h))
    if txt == "":
        return [w, h]
    else:
        txt = txt.split(",")
        return [int(txt[0]), int(txt[1])]

debug = True
# constantes internas: talla lienzo, camara, centro y gravedad
mat = preInicio(400, 600)
mat[1] = mat[1] if mat[1] >= mat[0] else mat[0]
cam = np.array([0, mat[0], mat[1] - mat[0] / 2], dtype=float)
cen = np.array([mat[0] / 2, mat[1] - mat[0] / 2], dtype=float)
acGrav = 9.0
# paso de rayo, colision^2 para luz, distancia sol, ancho zonas,
#   luz ambiente %, fuerza de luz 0-255, colision^2 para etc
cnfgluz = [6, 100, 100000, 50, 0.3, 255, 36]
# estructura de todos los voxels
pos = np.zeros((0, 3), dtype=float)
col = np.zeros((0, 4), dtype=int)
gru = np.zeros(0, dtype=int)
# guardado para retroceder una vez
memoria = []
# guardado para velocidad entre simulaciones
vel = []
# color actual para pintar al crear
acol = np.array([255, 255, 255, 255], dtype=int)
acol = [acol.copy(), acol.copy(), acol.copy()]
shadow = np.array([50, 50, 50, 40], dtype=int)
# gamas de color estandar y de animaciones
ecol = []
libro = []
# visibilidad de los grupos
gvis = np.zeros(0, dtype=int) == 0
# grupo actual (-1 todos)
mig = -1
# guarda el giro total dado
giro = 0
# banderas del juego
# autodraw, renderluz, absoluto, focal, picada, dibuplanos, verfondos
flags = [True, False, True, False, False, True, True]
# otras variables para dibujado
contorno = 1
luz = np.zeros(3, dtype=float)
# para ver demoras
reloj = 0
# escalamiento hecho a png durante exportacion
escalaimg = 1
# imagenes de fondo
fondos = [[False, False, False, False], [None, None, None, None]]
cuadricula = None
cuadrito = 24
# archivo ultimo que se guardo o abrio
archul = ""
# para acabar el software
salir = False

# funciones principales:

def main():
    global salir
    print("")
    print("***Creador Voxel Omarsaurico***")
    print("(ayuda)")
    print("")
    # inicializacion del display
    pg.init()
    inicializarWindow(0.8)
    luzDefecto()
    abrirTXT("config", True, False, True, False)
    dibujar(True)
    # hilo que procesa las entradas por consola
    hil = th(target=ciclo)
    hil.start()
    # ciclo para no bloquear el display
    while not salir:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                salir = True
    guardaConfig()
    print("***Finalizado***")
    print("")
    pg.quit()

def ciclo():
    global salir
    global debug
    while not salir:
        if debug:
            opciones()
        else:
            try:
                opciones()
            except:
                print("error")

def opciones():
    global salir
    global flags
    global luz
    global mig
    global cnfgluz
    global giro
    global contorno
    global escalaimg
    global archul
    pin = False
    sel = input(strG() + "-> ")
    # administracion
    if sel == "salir":
        salir = True
    elif sel == "atras" or sel == "z":
        retroceder()
        pin = True
    elif sel == "grupo":
        mig = inputGru()
        if flags[0]:
            dibujar(True)
    elif sel == "ver":
        dibujar(True)
    elif sel == "nuevo":
        mig = grupoVacio()
    elif sel == "visible":
        visibleGrupo(inputGru())
        pin = True
    elif sel == "exportar":
        n = input(tab() + "nombre de archivo: ").replace(" ", "")
        ang = inputCaras()
        modo = inputOpciones(lasExport(), 0)
        quest = input(tab() + "elegir animacion (s/N): ") == "s"
        if quest:
            ani, ok = elegirAnimacion(input(tab() + "nombre animacion: "))
        else:
            ani, ok = inputAnima()
        if ok:
            exportarPNG(n, ang, ani, modo)
    elif sel == "info":
        informacion()
    elif sel == "efectos":
        losEfectos()
    elif sel == "crear anima" or sel == "c anima":
        n = input(tab() + "nombre animacion: ")
        ani, ok = inputAnima()
        if ok:
            nuevaAnimacion(n, ani)
    elif sel == "borra anima" or sel == "b anima":
        n = input(tab() + "nombre animacion: ")
        eliminarAnimacion(n)
    elif sel == "ver anima":
        verAnimaciones()
    elif sel == "guardar":
        n = input(tab() + "nombre de archivo (vacio, {}): ".format(
            archul)).replace(" ", "")
        guardarTXT(n, True, True)
    elif sel == "guardar pieza":
        n = input(tab() + "nombre de archivo: ").replace(" ", "")
        guardarTXT(n, False)
    elif sel == "salvar" or sel == "s":
        guardarTXT("tmp", True)
    elif sel == "cargar":
        abrirTXT("tmp", True, True, True, True)
        pin = True
    elif sel == "abrir":
        n = input(tab() + "nombre de archivo: ").replace(" ", "")
        tx = input(tab() + "texturas (s/N): ") == "s"
        vx = not input(tab() + "voxels (S/n): ") == "n"
        cx = input(tab() + "configs (s/N): ") == "s"
        ax = input(tab() + "animaciones (s/N): ") == "s"
        abrirTXT(n, tx, vx, cx, ax, True)
        pin = True
    elif sel == "modelo":
        n = input(tab() + "nombre de archivo: ").replace(" ", "")
        abrirTXT(n, False, True, False, False)
        pin = True
    elif sel == "acercade":
        acercaDe()
    elif sel == "banderas":
        lasBanderas()
    elif sel == "autodraw":
        flags[0] = not flags[0]
        print(tab() + ("On" if flags[0] else "Off"))
        if flags[0]:
            dibujar()
    elif sel == "verfondos":
        flags[6] = not flags[6]
        print(tab() + ("On" if flags[6] else "Off"))
        if flags[0]:
            dibujar()
    elif sel == "dibuplanos":
        flags[5] = not flags[5]
        print(tab() + ("On" if flags[5] else "Off"))
        if flags[5]:
            borraPlanos()
        if flags[0]:
            dibujar()
    elif sel == "ayuda":
        laAyuda()
    elif sel == "renderluz":
        flags[1] = not flags[1]
        print(tab() + ("On" if flags[1] else "Off"))
        if flags[0]:
            dibujar()
    elif sel == "absoluto":
        flags[2] = not flags[2]
        print(tab() + ("On" if flags[2] else "Off"))
    elif sel == "picada":
        flags[4] = not flags[4]
        print(tab() + ("On" if flags[4] else "Off"))
        if flags[0]:
            dibujar()
    elif sel == "tipoluz":
        flags[3] = not flags[3]
        print(tab() + ("Foco" if flags[3] else "Sol"))
        if flags[0] and flags[1]:
            dibujar()
    elif sel == "sintaxis":
        sintaxis()
    elif sel == "escalapng":
        para, ok = inputVec(tab() + "porc: ", 1)
        if ok:
            escalaimg = para[0]
    elif sel == "fondos":
        inputFondos()
        if flags[0]:
            dibujar()
    # transformacion
    elif sel == "luz defecto":
        luzDefecto()
        pin = True
    elif sel == "girar":
        try:
            para = float(input(tab() + "ang: ").replace(" ", ""))
        except:
            para = 0
        giraTodo(para)
        if para != 0:
            pin = True
    elif sel == "d":
        giraTodo(45)
        pin = True
    elif sel == "a":
        giraTodo(-45)
        pin = True
    elif sel == "centrar":
        giraCentro()
        pin = True
    elif sel == "borra bajotierra" or sel == "b bajotierra":
        retenerCambio()
        eliminarBajotierra()
        pin = True
    elif sel == "borra grupo" or sel == "b grupo":
        retenerCambio()
        eliminarGrupo()
        pin = True
    elif sel == "mezclar":
        retenerCambio()
        mezclarGrupos(inputGru())
        pin = True
    elif sel == "duplicar":
        retenerCambio()
        duplicarGrupo()
        pin = True
    elif sel == "mover":
        para, ok = inputVec(tab() + "(x,y,z): ", 3)
        if ok:
            retenerCambio()
            traslacion(para)
            pin = True
    elif sel == "posicion":
        para, ok = inputVec(tab() + "(xi,yi,zi,xf,yf,zf): ", 6)
        if ok:
            retenerCambio()
            posicion(para[:3], para[3:6])
            pin = True
    elif sel == "escalar":
        para, ok = inputVec(tab() + "(xi,yi,zi,xm,ym,zm): ", 6)
        if ok:
            retenerCambio()
            escalamiento(para[:3], para[3:6])
            pin = True
    elif sel == "invertir":
        retenerCambio()
        escalamiento(np.array([0, 0, 0]), np.array([-1, 1, 1]))
        pin = True
    elif sel == "masa":
        masaCentro(True)
    elif sel == "borra colision" or sel == "b colision":
        retenerCambio()
        eliminarColision(inputGru())
        pin = True
    elif sel == "borra luz" or sel == "b luz":
        retenerCambio()
        eliminarLuz()
        pin = True
    elif sel == "borra taladro" or sel == "b taladro":
        para, ok = inputVec(tab() + "(xi,yi,zi,xf,yf,zf,rad): ", 7)
        if ok:
            retenerCambio()
            t = input(tab() + "hasta el final (s/N): ") == "s"
            eliminarRayo(para[:3], para[3:6], t, para[6])
            pin = True
    elif sel == "borra cercano" or sel == "b cercano":
        para, ok = inputVec(tab() + "radio^2 (def.20): ", 1)
        if ok:
            retenerCambio()
            eliminarColision(inputGru(), para[0])
            pin = True
    elif sel == "borra cruzados" or sel == "b cruzados":
        retenerCambio()
        eliminarColision(mig)
        pin = True
    elif sel == "rotar":
        para, ok = inputVec(tab() + "(xi,yi,zi,xg,yg,zg): ", 6)
        if ok:
            retenerCambio()
            rotacion(para[:3], para[3:6])
            pin = True
    elif sel == "espejo":
        para = input(tab() + "(ejex,ejey) (S/n,s/N): ").replace(" ", "").split(",")
        if len(para) == 2:
            retenerCambio()
            espejo(not para[0] == "n", para[1] == "s")
            pin = True
        else:
            print(tab() + "!!!")
    elif sel == "posicion luz":
        if flags[0]:
            dibujar(True)
        if flags[2]:
            giraLuz(-giro)
        para, ok = inputVec(tab() + "(x,y,z) ({},{},{}): ".format(
            int(luz[0]), int(luz[1]), int(luz[2])), 3)
        if flags[2]:
            giraLuz(giro)
        if ok:
            trasladaLuz(para)
            if flags[0]:
                dibujar(True)
    elif sel == "rotar luz":
        para, ok = inputVec(tab() + "(ang): ", 1)
        if ok:
            retenerCambio()
            giraLuz(para[0])
            pin = True
    elif sel == "borra cilindro" or sel == "b cilindro":
        para, ok = inputVec(tab() + "(x,y,z,rad,alt,eje): ", 6)
        if ok:
            retenerCambio()
            inv = input(tab() + "invertido (s/N): ") == "s"
            eliminarCilindro(para[:3], para[3], para[4], para[5], inv)
            pin = True
    elif sel == "borra esfera" or sel == "b esfera":
        para, ok = inputVec(tab() + "(x,y,z,rad): ", 4)
        if ok:
            retenerCambio()
            inv = input(tab() + "invertido (s/N): ") == "s"
            eliminarEsfera(para[:3], para[3], inv)
            pin = True
    elif sel == "borra caja" or sel == "b caja":
        para, ok = inputVec(tab() + "(x,y,z,anch,larg,alt): ", 6)
        if ok:
            retenerCambio()
            inv = input(tab() + "invertido (s/N): ") == "s"
            eliminarCaja(para[:3], para[3:6], inv)
            pin = True
    elif sel == "borra azar" or sel == "b azar":
        para, ok = inputVec(tab() + "porc: ", 1)
        if ok:
            retenerCambio()
            eliminarAzar(np.clip(para[0], 0, 1))
            pin = True
    elif sel == "revolucion":
        if mig != -1:
            retenerCambio()
            revolucion()
            pin = True
    elif sel == "estruir":
        if mig != -1:
            para, ok = inputVec(tab() + "(alt,eje): ", 2)
            if ok:
                retenerCambio()
                estrucion(para[0], para[1])
                pin = True
    elif sel == "limitar":
        retenerCambio()
        limitar()
        pin = True
    elif sel == "tierra":
        retenerCambio()
        limitar(True)
        pin = True
    elif sel == "borra limite" or sel == "b limite":
        retenerCambio()
        eliminarLimites()
        pin = True
    elif sel == "sim azar":
        retenerCambio()
        while True:
            particulasAzar()
            if flags[0]:
                dibujar()
            if input(tab() + "repetir (S/n): ") == "n":
                break
    elif sel == "sim velocidad":
        retenerCambio()
        r = input(tab() + "reiniciar (s/N): ") == "s"
        while True:
            particulasVelcidad(r)
            if flags[0]:
                dibujar()
            r = False
            if input(tab() + "repetir (S/n): ") == "n":
                break
    elif sel == "sim foco":
        para, ok = inputVec(tab() + "(x,y,z): ", 3)
        if ok:
            retenerCambio()
            a = not input(tab() + "atraer (S/n): ") == "n"
            while True:
                particulasDireccionadas(para[:3], a)
                if flags[0]:
                    dibujar()
                if input(tab() + "repetir (S/n): ") == "n":
                    break
    elif sel == "sim colision":
        retenerCambio()
        g = inputGru()
        a = input(tab() + "auto iterar (s/N): ") == "s"
        if a:
            para, ok = inputVec(tab() + "iteraciones max: ", 1)
        else:
            para = [1]
            ok = True
        if ok:
            particulasLibres(g, para[0], not a)
    elif sel == "sim gravedad":
        retenerCambio()
        while True:
            particulasGravedad()
            if flags[0]:
                dibujar()
            if input(tab() + "repetir (S/n): ") == "n":
                break
    elif sel == "sim enjambre":
        para, ok = inputVec(tab() + "(x,y,z): ", 3)
        if ok:
            retenerCambio()
            para, ok = inputVec(tab() + "iteraciones max: ", 1)
            if ok:
                g = inputGru()
                a = not input(tab() + "atraer (S/n): ") == "n"
                r = input(tab() + "reiniciar (s/N): ") == "s"
                while True:
                    particulasEnjambre(g, para[:3], a, para[0], r)
                    if flags[0]:
                        dibujar()
                    r = False
                    if input(tab() + "repetir (S/n): ") == "n":
                        break
    elif sel == "sim demoler":
        retenerCambio()
        para, ok = inputVec(tab() + "iteraciones max: ", 1)
        if ok:
            g = inputGru()
            while True:
                particulasDemoler(g, para[0])
                if flags[0]:
                    dibujar()
                if input(tab() + "repetir (S/n): ") == "n":
                    break
    elif sel == "sim torcion":
        para, ok = inputVec(tab() + "(x,y,z): ", 3)
        if ok:
            retenerCambio()
            a = not input(tab() + "agregar azar (S/n): ") == "n"
            while True:
                particulasTorcion(para[:3], a)
                if flags[0]:
                    dibujar()
                if input(tab() + "repetir (S/n): ") == "n":
                    break
    elif sel == "sim tornado":
        retenerCambio()
        para, ok = inputVec(tab() + "iteraciones max: ", 1)
        if ok:
            g = inputGru()
            while True:
                particulasTornado(g, para[0])
                if flags[0]:
                    dibujar()
                if input(tab() + "repetir (S/n): ") == "n":
                    break
    elif sel == "anomalias":
        para, ok = inputVec(tab() + "porc: ", 1)
        if ok:
            retenerCambio()
            crearAnomalias(np.clip(para[0], 0, 1))
            pin = True
    elif sel == "clon linea":
        para, ok = inputVec(tab() + "(x,y,z,paso): ", 4)
        if ok:
            retenerCambio()
            clonLinea(para[:3], para[3])
            pin = True
    elif sel == "clon aro":
        para, ok = inputVec(tab() + "(x,y,ang): ", 3)
        if ok:
            retenerCambio()
            clonAro(np.array([para[0], para[1], 0]), para[2])
            pin = True
    # creacion
    elif sel == "crear demo" or sel == "c demo" or sel == "demo":
        retenerCambio()
        crearDemo()
        pin = True
    elif sel == "crear poligono" or sel == "c poligono":
        para, ok = inputPuntos()
        if ok:
            retenerCambio()
            crearPoligono(para, input(tab() + "cerrar (s/N): ") == "s")
            pin = True
    elif sel == "crear punto" or sel == "c punto":
        para, ok = inputVec(tab() + "(x,y,z): ", 3)
        if ok:
            retenerCambio()
            crearPunto(para)
            pin = True
    elif sel == "crear relleno" or sel == "c relleno":
        para, ok = inputVec(tab() + "(x,y,z): ", 3)
        if ok:
            retenerCambio()
            crearRelleno(para, inputGru(), para)
            pin = True
    elif sel == "crear mancha" or sel == "c mancha":
        para, ok = inputVec(tab() + "(x,y,z): ", 3)
        if ok:
            retenerCambio()
            crearMancha(para, inputGru(), para)
            pin = True
    elif sel == "crear aro" or sel == "c aro":
        para, ok = inputVec(tab() + "(x,y,z,rad,eje): ", 5)
        if ok:
            retenerCambio()
            crearAro(para[:3], para[3], para[4])
            pin = True
    elif sel == "crear circulo" or sel == "c circulo":
        para, ok = inputVec(tab() + "(x,y,z,rad,eje): ", 5)
        if ok:
            retenerCambio()
            crearCirculo(para[:3], para[3], para[4])
            pin = True
    elif sel == "crear marco" or sel == "c marco":
        para, ok = inputVec(tab() + "(x,y,z,anch,larg,eje): ", 6)
        if ok:
            retenerCambio()
            crearMarco(para[:3], para[3:5], para[5])
            pin = True
    elif sel == "crear cuadro" or sel == "c cuadro":
        para, ok = inputVec(tab() + "(x,y,z,anch,larg,eje): ", 6)
        if ok:
            retenerCambio()
            crearCuadro(para[:3], para[3:5], para[5])
            pin = True
    elif sel == "crear caja" or sel == "c caja":
        para, ok = inputVec(tab() + "(x,y,z,anch,larg,alt,eje): ", 7)
        if ok:
            retenerCambio()
            crearCaja(para[:3], para[3:6], para[6])
            pin = True
    elif sel == "crear piramide" or sel == "c piramide":
        para, ok = inputVec(tab() + "(x,y,z,anch,larg,alt,eje): ", 7)
        if ok:
            retenerCambio()
            crearPiramide(para[:3], para[3:6], para[6])
            pin = True
    elif sel == "crear cilindro" or sel == "c cilindro":
        para, ok = inputVec(tab() + "(x,y,z,rad,alt,eje): ", 6)
        if ok:
            retenerCambio()
            crearCilindro(para[:3], para[3], para[4], para[5])
            pin = True
    elif sel == "crear esfera" or sel == "c esfera":
        para, ok = inputVec(tab() + "(x,y,z,rad): ", 4)
        if ok:
            retenerCambio()
            crearEsfera(para[:3], para[3])
            pin = True
    elif sel == "crear cono" or sel == "c cono":
        para, ok = inputVec(tab() + "(x,y,z,rad,alt,eje): ", 6)
        if ok:
            retenerCambio()
            crearCono(para[:3], para[3], para[4], para[5])
            pin = True
    elif sel == "crear solido caja" or sel == "c solido caja":
        para, ok = inputVec(tab() + "(x,y,z,anch,larg,alt,eje): ", 7)
        if ok:
            retenerCambio()
            crearCaja(para[:3], para[3:6], para[6], True)
            pin = True
    elif sel == "crear solido piramide" or sel == "c solido piramide":
        para, ok = inputVec(tab() + "(x,y,z,anch,larg,alt,eje): ", 7)
        if ok:
            retenerCambio()
            crearPiramide(para[:3], para[3:6], para[6], True)
            pin = True
    elif sel == "crear solido cilindro" or sel == "c solido cilindro":
        para, ok = inputVec(tab() + "(x,y,z,rad,alt,eje): ", 6)
        if ok:
            retenerCambio()
            crearCilindro(para[:3], para[3], para[4], para[5], True)
            pin = True
    elif sel == "crear solido esfera" or sel == "c solido esfera":
        para, ok = inputVec(tab() + "(x,y,z,rad): ", 4)
        if ok:
            retenerCambio()
            crearEsfera(para[:3], para[3], True)
            pin = True
    elif sel == "crear solido cono" or sel == "c solido cono":
        para, ok = inputVec(tab() + "(x,y,z,rad,alt,eje): ", 6)
        if ok:
            retenerCambio()
            crearCono(para[:3], para[3], para[4], para[5], True)
            pin = True
    elif sel == "crear palo" or sel == "c palo":
        para, ok = inputVec(tab() + "(x,y,z,alt,eje): ", 5)
        if ok:
            retenerCambio()
            crearCilindro(para[:3], 0, para[3], para[4])
            pin = True
    elif sel == "crear silueta" or sel == "c silueta":
        retenerCambio()
        crearSilueta()
        pin = True
    elif sel == "crear sombra" or sel == "c sombra":
        retenerCambio()
        crearSombra()
        pin = True
    elif sel == "crear rayo" or sel == "c rayo":
        para, ok = inputVec(tab() + "(xi,yi,zi,xf,yf,zf): ", 6)
        if ok:
            retenerCambio()
            crearRayo(para[:3], para[3:6])
            pin = True
    elif sel == "crear azar cilindro" or sel == "c azar cilindro":
        para, ok = inputVec(tab() + "(x,y,z,rad,alt,eje,porc): ", 7)
        if ok:
            retenerCambio()
            crearAzarCilindro(para[:3], para[3], para[4], para[5],
                              np.clip(para[6], 0, 1))
            pin = True
    elif sel == "crear azar esfera" or sel == "c azar esfera":
        para, ok = inputVec(tab() + "(x,y,z,rad,porc): ", 5)
        if ok:
            retenerCambio()
            crearAzarEsfera(para[:3], para[3], np.clip(para[4], 0, 1))
            pin = True
    elif sel == "crear arbol" or sel == "c arbol":
        t = inputOpciones(losArboles(), 0)
        para, ok = inputVec(tab() + "(x,y,z,alt,radTronco,radCopa): ", 6)
        if ok:
            retenerCambio()
            crearArbol(para[:3], para[3], para[4], para[5], t)
            pin = True
    elif sel == "crear rueda" or sel == "c rueda":
        para, ok = inputVec(tab() + "(x,y,z,rad,anch): ", 5)
        if ok:
            retenerCambio()
            crearRueda(para[:3], para[3], para[4])
            pin = True
    elif sel == "crear paredes" or sel == "c paredes":
        print(tab() + "solo (x,y)")
        para, ok = inputPuntos()
        if ok:
            paraa, ok = inputVec(tab() + "(z,alt)", 2)
            if ok:
                retenerCambio()
                crearParedes(para, paraa[0], paraa[1],
                           input(tab() + "cerrar (s/N): ") == "s")
                pin = True
    elif sel == "crear revolucion" or sel == "c revolucion":
        print(tab() + "solo (x,z)")
        para, ok = inputPuntos()
        if ok:
            retenerCambio()
            crearRevolucion(para, input(tab() + "cerrar (s/N): ") == "s")
            pin = True
    elif sel == "crear obra" or sel == "c obra":
        img, ok = inputImg()
        if ok:
            retenerCambio()
            obraPNG(img)
            pin = True
    elif sel == "crear techo" or sel == "c techo":
        para, ok = inputVec(tab() + "(x,y,z,anch,larg,alt): ", 6)
        if ok:
            retenerCambio()
            crearTecho(para[:3], para[3:6])
            pin = True
    elif sel == "crear rampa" or sel == "c rampa":
        para, ok = inputVec(tab() + "(x,y,z,larg,anch,alt,ang): ", 7)
        if ok:
            retenerCambio()
            crearRampa(para[:3], para[3:6], para[6])
            pin = True
    elif sel == "crear pelo" or sel == "c pelo":
        para, ok = inputVec(tab() + "(xi,yi,zi,xd,yd,zd,larg,porc): ", 8)
        if ok:
            g = not input(tab() + "gravedad (S/n): ") == "n"
            if input(tab() + "foco (s/N): ") == "s":
                foc, ok = inputVec(tab() + "(x,y,z,porc): ", 4)
                foc[3] = np.clip(foc[3], 0, 1)
                if ok:
                    retenerCambio()
                    crearPelo(para[:3], para[3:6], para[6],
                              np.clip(para[7], 0, 1), g, [foc])
                    pin = True
            else:
                retenerCambio()
                crearPelo(para[:3], para[3:6], para[6], np.clip(para[7], 0, 1), g)
                pin = True
    elif sel == "crear monigote" or sel == "c monigote":
        print(tab() + "base, cabeza, frente, altura")
        para, ok = inputVec(tab() + "(xb,yb,zb,xc,yc,zc,xf,yf,zf,alt): ", 10)
        if ok:
            extrem = []
            aux, ok = inputVec(tab() + "pies (xi,yi,zi,xd,yd,zd): ", 6)
            if ok:
                extrem.append(aux[:3])
                extrem.append(aux[3:6])
                aux, ok = inputVec(tab() + "manos (xi,yi,zi,xd,yd,zd): ", 6)
                if ok:
                    extrem.append(aux[:3])
                    extrem.append(aux[3:6])
                    fem = inputOpciones(forMoni(), 0)
                    retenerCambio()
                    crearMonigote(para[:3], para[3:6], para[6:9],
                                  extrem, fem, para[9])
                    pin = True
    elif sel == "crear loco" or sel == "c loco":
        print(tab() + "base, altura")
        para, ok = inputVec(tab() + "(xb,yb,zb,alt): ", 4)
        if ok:
            extrem = []
            l1 = (np.random.random_sample(3) * 2.0 - 1.0) * para[3]
            extrem.append(para[:3] + l1)
            l1 = (np.random.random_sample(3) * 2.0 - 1.0) * para[3]
            extrem.append(para[:3] + l1)
            l1 = (np.random.random_sample(3) * 2.0 - 1.0) * para[3]
            extrem.append(para[:3] + l1)
            l1 = (np.random.random_sample(3) * 2.0 - 1.0) * para[3]
            extrem.append(para[:3] + l1)
            fem = inputOpciones(forMoni(), 0)
            retenerCambio()
            l1 = np.random.random_sample(3) * 2.0 - 1.0
            l2 = np.random.random_sample(3) * 2.0 - 1.0
            crearMonigote(para[:3], l1, l2, extrem, fem, para[3])
            pin = True
    elif sel == "crear maniqui" or sel == "c maniqui":
        para, ok = inputVec(tab() + "(x,y,z,alt,ang): ", 5)
        if ok:
            retenerCambio()
            bra = inputOpciones(losBrazos(), 3)
            crearManiqui(para[:3], para[3], bra, para[4])
            pin = True
    # dibujado
    elif sel == "color azar":
        colorAzar(input(tab() + "payaso (s/N): ") == "s")
    elif sel == "color":
        c1, ok = inputCol(1)
        if ok:
            c2, ok = inputCol(2)
            if ok:
                c3, ok = inputCol(3)
                if ok:
                    nuevoColor(c1, c2, c3)
    elif sel == "crear textura" or sel == "c textura":
        n = input(tab() + "nombre color: ")
        if input(tab() + "color actual (s/N): ") == "s":
            nuevaTextura(n, acol[0], acol[1], acol[2])
        else:
            c1, ok = inputCol(1)
            if ok:
                c2, ok = inputCol(2)
                if ok:
                    c3, ok = inputCol(3)
                    if ok:
                        nuevaTextura(n, c1, c2, c3)
    elif sel == "ver texturas":
        verTexturas()
    elif sel == "borra textura" or sel == "b textura":
        n = input(tab() + "nombre color (-1 all): ")
        eliminarTextura(n)
    elif sel == "textura":
        n = input(tab() + "nombre color: ")
        elegirTextura(n)
    elif sel == "pintar":
        retenerCambio()
        pintarGrupo()
        pin = True
    elif sel == "pintar textura" or sel == "p textura":
        retenerCambio()
        pintarClasico(input(tab() + "nombre color: "))
        pin = True
    elif sel == "efecto color":
        retenerCambio()
        efectoColor(inputOpciones(operaPixel(), 4))
        pin = True
    elif sel == "render":
        dibujar()
    elif sel == "galeria":
        galeriaTexturas()
    elif sel == "contorno":
        contorno = inputOpciones(losContornos(), 1)
        pin = True
    elif sel == "brocha cilindro":
        para, ok = inputVec(tab() + "(x,y,z,rad,alt,eje): ", 6)
        if ok:
            retenerCambio()
            inv = input(tab() + "invertido (s/N): ") == "s"
            brochaCilindro(para[:3], para[3], para[4], para[5], inv)
            pin = True
    elif sel == "brocha esfera":
        para, ok = inputVec(tab() + "(x,y,z,rad): ", 4)
        if ok:
            retenerCambio()
            inv = input(tab() + "invertido (s/N): ") == "s"
            brochaEsfera(para[:3], para[3], inv)
            pin = True
    elif sel == "brocha caja":
        para, ok = inputVec(tab() + "(x,y,z,anch,larg,alt): ", 6)
        if ok:
            retenerCambio()
            inv = input(tab() + "invertido (s/N): ") == "s"
            brochaCaja(para[:3], para[3:6], inv)
            pin = True
    elif sel == "brocha azar":
        para, ok = inputVec(tab() + "porc: ", 1)
        if ok:
            retenerCambio()
            brochaAzar(np.clip(para[0], 0, 1))
            pin = True
    elif sel == "fuerza luz":
        para, ok = inputVec(tab() + "porc (ambiente,luz) ({},{}): ".format(
            cnfgluz[4], cnfgluz[5] / 255), 2)
        if ok:
            para = np.clip(para, 0, 1)
            modificaLuz(para[0], para[1])
    elif sel == "filtro":
        retenerCambio()
        filtroColor()
        pin = True
    elif sel == "poner alfa":
        para, ok = inputVec(tab() + "alfa (0-255): ", 1)
        if ok:
            retenerCambio()
            pintarTransparencia(para[0], True)
            pin = True
    elif sel == "escalar alfa":
        para, ok = inputVec(tab() + "factor alfa: ", 1)
        if ok:
            retenerCambio()
            pintarTransparencia(para[0], False)
            pin = True
    elif sel == "pintar luz":
        retenerCambio()
        pintarLuz()
        pin = True
    elif sel == "pintar sombra":
        retenerCambio()
        pintarSombra()
        pin = True
    else:
        if not salir:
            print(tab() + "???")
    # autodibujado continuamente
    if flags[0] and pin:
        dibujar()
    print("")

# funciones de ingreso de datos:

def inputImg():
    img = None
    ok = True
    try:
        txt = input(tab() + "nombre archivo png: ").replace(".png", "")
        img = pg.image.load(txt + ".png")
    except:
        img = None
        ok = False
        print(tab() + "!!!")
    return img, ok

def inputPuntos():
    pnts = []
    ok = True
    n = 0
    while True:
        txt = input(tab() + str(n) + " (x,y,z): ").replace(" ", "")
        txt = clavesInput(txt)
        if txt == "":
            if len(pnts) == 0:
                ok = False
            break
        if txt == "x":
            if len(pnts) > 0:
                pnts.pop(-1)
        else:
            uk = True
            try:
                txt = np.fromstring(txt, dtype=float, sep=",")
                if txt.size == 2:
                    txt = np.array([txt[0], txt[1], 0], dtype=float)
                elif txt.size != 3:
                    uk = False
            except:
                uk = False
            if uk:
                pnts.append(txt)
                n += 1
    return pnts, ok

def inputVec(msj, tot):
    global mig
    para = input(msj).replace(" ", "")
    para = clavesInput(para)
    ok = True
    try:
        para = np.fromstring(para, dtype=float, sep=",")
        if para.size != tot:
            ok = False
    except:
        ok = False
    if not ok:
        para = np.ones(tot, dtype=float)
        print(tab() + "!!!")
    return para, ok

def inputGru(opc=""):
    global mig
    global gvis
    g = input(tab() + opc + "id grupo (-1 a {}): ".format(gvis.size - 1))
    g = g.replace(" ", "")
    try:
        g = int(g)
        if not (g == -1 or (g >= 0 and g < gvis.size)):
            g = mig
    except:
        g = mig
    return g

def inputCol(ind):
    txt = input(tab() + "c{} (r,g,b,a) (0-255): ".format(ind)).replace(" ", "")
    ok = True
    c = np.array([255, 255, 255, 255], dtype=int)
    if len(txt) > 0:
        try:
            c = np.clip(np.fromstring(txt, dtype=int, sep=","), 0, 255)
            if c.size == 3:
                c = np.append(c, 255)
            elif c.size != 4:
                ok = False
        except:
            ok = False
        if not ok:
            c = np.array([255, 255, 255, 255], dtype=int)
            print(tab() + "!!!")
    return c, ok

def inputOpciones(opc, defecto):
    txt = " ".join(opc)
    con = input(tab() + "(" + txt + "): ").replace(" ", "")
    try:
        con = int(con)
        if not (con >= 0 and con < len(opc)):
            con = defecto
    except:
        con = defecto
    return con

def inputCaras():
    ang = input(tab() + "lados (0->1 1->4 2->8 3->16 4->32): ")
    ang = ang.replace(" ", "")
    if ang == "1":
        ang = 4
    elif ang == "2":
        ang = 8
    elif ang == "3":
        ang = 16
    elif ang == "4":
        ang = 32
    else:
        ang = 1
    return ang

def inputAnima():
    txt = input(tab() + "animacion (s/N): ") == "s"
    ani = [txt]
    ok = True
    try:
        if txt:
            txt = min(32, max(1, int(input(tab() + "pasos (1 a 32): "))))
            ani.append(txt)
            n = 0
            while input(tab() + "-> anima " + str(n) + " (s/N): ") == "s":
                mov = [inputGru("   ")]
                sel = input(tab() + "   tipo: ")
                mov.append(sel)
                if sel == "":
                    pass
                else:
                    kill()
                ani.append(mov)
                n += 1
    except:
        ok = False
        ani = [False]
    return ani, ok

def inputFondos():
    global fondos
    nms = ["3D", "lado", "frente", "superior"]
    for f in range(4):
        txt = input(tab() + "nombre archivo png para vista (" + nms[f] + "): ")
        txt = txt.replace(" ", "").replace(".png", "")
        if len(txt) == 0:
            fondos[0][f] = False
            fondos[1][f] = None
        elif os.path.exists(txt + ".png"):
            ss = pg.image.load(txt + ".png").convert()
            fondos[0][f] = True
            fondos[1][f] = ss
        else:
            fondos[0][f] = False
            fondos[1][f] = None
    escalarFondos()

# funciones de herramientas internas:

def clavesInput(parametro):
    global mig
    global cuadrito
    global mat
    para = parametro
    n = 0
    while para.count("masa") > 0:
        amig = mig
        mig = inputGru("m" + str(n) + ", ")
        n += 1
        des, base, mas = masaCentro(False)
        mig = amig
        para = para.replace("masa", "{},{},{}".format(des[0], des[1], des[2]), 1)
    n = 0
    while para.count("base") > 0:
        amig = mig
        mig = inputGru("b" + str(n) + ", ")
        n += 1
        des, base, mas = masaCentro(False)
        mig = amig
        para = para.replace("base", "{},{},{}".format(des[0], des[1], base), 1)
    n = 0
    while para.count("tierra") > 0:
        amig = mig
        mig = inputGru("t" + str(n) + ", ")
        n += 1
        des, base, mas = masaCentro(False)
        mig = amig
        para = para.replace("tierra", "{},{},0".format(des[0], des[1]), 1)
    if para.count("ori") > 0:
        para = para.replace("ori", "0,0,0")
    while para.count("rf") > 0:
        para = para.replace("rf", "{}".format(np.random.ranf() * 2.0 - 1.0), 1)
    while para.count("rp") > 0:
        para = para.replace("rp", "{}".format(np.random.ranf()), 1)
    while para.count("ru") > 0:
        ch = [-cuadrito, 0, cuadrito]
        ch = ch[np.random.randint(0, 3)]
        para = para.replace("ru", "{}".format(ch), 1)
    while para.count("rs") > 0:
        para = para.replace("rs", "{}".format(np.random.ranf() * (mat[0] / 2)), 1)
    while para.count("azar") > 0:
        para = para.replace("azar", "{},{},{}".format(
            np.random.randint(-int(mat[0] / 2), int(mat[0] / 2)),
            np.random.randint(-int(mat[0] / 2), int(mat[0] / 2)),
            np.random.randint(0, int(mat[1] - mat[0]))), 1)
    while para.count("rand") > 0:
        para = para.replace("rand", "{},{},{}".format(
            np.random.randint(-int(mat[0] / 3), int(mat[0] / 3)),
            np.random.randint(-int(mat[0] / 3), int(mat[0] / 3)),
            np.random.randint(0, int((mat[1] - mat[0]) * 0.8))), 1)
    vec = para.split(",")
    for v in range(len(vec)):
        if "u" in vec[v]:
            if vec[v] == "u":
                vec[v] = str(cuadrito)
            elif vec[v] == "-u":
                vec[v] = str(-cuadrito)
            else:
                try:
                    vec[v] = str(cuadrito * float(vec[v].replace("u", "")))
                except:
                    vec[v] = "0"
    para = ",".join(vec)
    return para

def kill():
    return "la vida esta sobrevaorada" + 69

def guardaConfig():
    global gvis
    gvis = np.zeros(gvis.size, dtype=int) == 1
    guardarTXT("config", False)

def version():
    return "(v0.1.0)"

def escalarFondos():
    global fondos
    global mat
    global pos
    global gru
    surf = pg.display.get_surface()
    tll = surf.get_size()
    tll = (int((tll[0] - 40) / 2), int(tll[1] - 20))
    for f in range(4):
        if fondos[0][f]:
            if f == 0:
                esc = tll
            elif f == 3:
                esc = (int(tll[0] / 2), int(tll[0] / 2))
            else:
                esc = tll[1] / mat[1]
                apos = pos.copy()
                agru = gru.copy()
                pos = np.zeros((0, 3), dtype=float)
                gru = np.zeros(0, dtype=int)
                s, v = dibujaPlanos(0)
                pos = apos
                gru = agru
                esc = (int(tll[0] / 2), int((s.get_size()[1] * esc) / 2))
            fondos[1][f] = pg.transform.smoothscale(fondos[1][f], esc)

def inicializarWindow(alto):
    global cen
    global mat
    global cuadricula
    global cuadrito
    pg.display.set_icon(icono())
    pg.display.set_caption("OmiVoxel")
    r = mat[0] / mat[1]
    hhh = pg.display.Info().current_h * alto
    w = ((hhh - 20) * r) * 2 + 40
    www = min(pg.display.Info().current_w * 0.95, w)
    pg.display.set_mode((int(www), int(hhh)))
    surf = pg.display.get_surface()
    surf.fill((0, 0, 0, 255))
    ss = paleta()
    px = surf.get_size()[0] - (ss.get_size()[0] + 10)
    py = surf.get_size()[1] - (ss.get_size()[1] + 10)
    surf.blit(ss, (px, py))
    pg.display.flip()
    # crear la cuadricula
    cuadricula = pg.Surface(mat, pg.SRCALPHA, 32)
    cuadricula.fill((0, 0, 0, 0))
    cc = (50, 50, 50, 150)
    for x in range(-max(mat), max(mat) + 1, cuadrito):
        pg.draw.line(cuadricula, cc,
                     cen + np.array([x, -max(mat)]),
                     cen + np.array([x, max(mat)]))
    for y in range(-max(mat), max(mat) + 1, cuadrito):
        pg.draw.line(cuadricula, cc,
                     cen + np.array([-max(mat), y]),
                     cen + np.array([max(mat), y]))
    cuadricula = pg.transform.smoothscale(cuadricula,
                                          (int(mat[0] / 2), int(mat[1] / 2)))

def icono():
    global mig
    global pos
    global col
    global gru
    global gvis
    global contorno
    global flags
    global debug
    global cen
    retenerCambio()
    pos = np.zeros((0, 3), dtype=float)
    col = np.zeros((0, 4), dtype=int)
    gru = np.zeros(0, dtype=int)
    gvis = np.zeros(0, dtype=int) == 0
    acontorno = contorno
    contorno = 4
    amig = mig
    aflags = flags.copy()
    flags[1] = False
    flags[4] = False
    agiro = giraCentro()
    g1 = grupoVacio()
    mig = g1
    crearCaja(np.array([-30, -30, 0]), np.array([60, 60, 20]), 2)
    pintarClasico("caqui")
    g2 = grupoVacio()
    mig = g2
    crearCilindro(np.zeros(3), 10, 30, 2)
    pintarClasico("agua")
    g3 = grupoVacio()
    mig = g3
    crearEsfera(np.array([0, 0, 50]), 15)
    pintarClasico("payaso")
    giraTodo(22.5)
    mig = g1
    mezclarGrupos(g2)
    mezclarGrupos(g3)
    ss = pg.Surface((128, 128), pg.SRCALPHA, 32)
    s = dibujaBasico()
    ss.blit(s, (0, 0), (cen[0] - 64, cen[1] - 85, 128, 128))
    ss = pg.transform.smoothscale(ss, (64, 64))
    if debug:
        pg.image.save(ss, "icono.png")
    giraCentro()
    giraTodo(agiro)
    mig = amig
    flags = aflags
    contorno = acontorno
    retroceder()
    return ss

def paleta():
    global debug
    global mat
    ss = pg.Surface((40, 36), pg.SRCALPHA, 32)
    for h in range(36):
        for l in range(36):
            pg.draw.rect(ss, hsl2rgb((h / 35) * 360, 0, l / 35),
                         (h, l, 1, 1))
    for i in range(36):
        ccc = int((i / 35) * 255)
        pg.draw.rect(ss, (ccc, ccc, ccc, 255),
                     (36, i, 4, 1))
    esc = int(mat[0] * 0.25)
    ss = pg.transform.smoothscale(ss, (int(esc * (40 / 36)), esc))
    ss = pg.transform.flip(ss, False, True)
    if debug:
        pg.image.save(ss, "paleta.png")
    return ss

def puntosTraslucidos():
    # seleccionados
    s1 = pg.Surface((12, 12), pg.SRCALPHA, 32)
    s1.fill((0, 0, 0, 0))
    pg.draw.circle(s1, (255, 255, 255, 20), (6, 6), 5)
    pg.draw.circle(s1, (0, 0, 0, 10), (6, 6), 6, 1)
    # no seleccionados
    s2 = pg.Surface((12, 12), pg.SRCALPHA, 32)
    s2.fill((0, 0, 0, 0))
    pg.draw.circle(s2, (255, 100, 100, 50), (6, 6), 5)
    pg.draw.circle(s2, (0, 0, 0, 25), (6, 6), 6, 1)
    # foco de luz y su base
    s3 = pg.Surface((16, 16), pg.SRCALPHA, 32)
    s3.fill((0, 0, 0, 0))
    pg.draw.circle(s3, (255, 255, 0, 200), (6, 6), 8)
    # centro y angulo
    s4 = pg.Surface((16, 16), pg.SRCALPHA, 32)
    s4.fill((0, 0, 0, 0))
    pg.draw.circle(s4, (0, 0, 0, 200), (6, 6), 5)
    sv = [s4, s3]
    return s1, s2, sv

def cronometro(opc="", show=True, forzado=False):
    global reloj
    global debug
    r = pg.time.get_ticks()
    if show and (debug or forzado):
        seg = (r - reloj) / 1000
        print(tab() + "..." + str(int(seg)) + "s " + opc)
    reloj = r

def modificaLuz(ambi, porc):
    global cnfgluz
    cnfgluz[4] = np.clip(ambi, 0, 1)
    cnfgluz[5] = int(np.clip(porc * 255, 0, 255))

def vecUniCruz(v1, v2):
    v3 = np.cross(v1, v2)
    v3 = v3 / magnitud(v3)
    return v3

def volVox():
    return (4 / 3) * np.pi * np.power(6, 3.0)

def magnitud(vec):
    return np.sqrt(np.power(vec, 2.0).sum())

def losContornos():
    return ["0->not", "1->neg", "2->opa", "3->miC", "4->liC",
            "5->diC", "6->C/2"]

def losArboles():
    return ["0->esf", "1->esfR", "2->tub", "3->tubR", "4->cono",
            "5->pino", "6->palo"]

def lasExport():
    return ["0->vector", "1->tiras", "2->matrix", "3->separados",
            "4->txt", "5->gif", "6->nada"]

def losBrazos():
    return ["0->nada", "1->frente", "2->lados", "3->abajo", "4->arriba"]

def operaPixel():
    return ["0->grises", "1->B/N", "2->negativo", "3->promSel",
            "4->variar", "5->azar", "6->azar3", "7->cambiar"]

def forMoni():
    return ["0->fem", "1->stick", "2->masc"]

def tab():
    return "     "

def strG():
    global mig
    ret = str(mig)
    return ret if len(ret) == 2 else " " + ret

def retenerCambio():
    global pos
    global col
    global gru
    global giro
    global gvis
    global memoria
    memoria.append([giro, pos.copy(), col.copy(), gru.copy(), gvis.copy()])
    if len(memoria) > 6:
        memoria.pop(0)

def verificarGrupos():
    global gru
    global gvis
    global mig
    if gru.size == 0:
        gvis = np.zeros(0, dtype=int) == 0
        mig = -1
    else:
        m = gru.max()
        while gvis.size <= m:
            gvis = np.append(gvis, True)
        if gvis.size > m + 1:
            gvis = gvis[:(m + 1)]
        if mig >= gvis.size:
            mig = -1

def pintar():
    global acol
    return acol[np.random.randint(3)]

def hsl2rgb(h, s, l):
    # 0<=h<360, 0<=s<=1, 0<=l<=1
    c = (1.0 - np.abs(2.0 * l - 1.0) * s)
    x = c * (1.0 - np.abs(np.mod(h / 60.0, 2.0) - 1.0))
    m = l - c / 2.0
    if h >= 0 and h < 60:
        rgb = [c, x, 0]
    elif h >= 60 and h < 120:
        rgb = [x, c, 0]
    elif h >= 120 and h < 180:
        rgb = [0, c, x]
    elif h >= 180 and h < 240:
        rgb = [0, x, c]
    elif h >= 240 and h < 300:
        rgb = [x, 0, c]
    else:
        rgb = [c, 0, x]
    ccc = np.array([(rgb[0] + m) * 255, (rgb[1] + m) * 255,
                    (rgb[2] + m) * 255, 255], dtype=int)
    return np.clip(ccc, 0, 255)

def agregar(p, c, g):
    global pos
    global col
    global gru
    pos = np.append(pos, giroAbs(p), axis=0)
    col = np.append(col, c, axis=0)
    gru = np.append(gru, g)
    verificarGrupos()

def grupoVacio():
    global gru
    if gru.size == 0:
        return 0
    else:
        m = gru.max()
        res = m + 1
        for v in range(m):
            if not v in gru:
                res = v
                break
        return res

def vecGrupo(talla, grupo):
    return np.zeros(talla, dtype=int) + grupo

def vecPintar(talla):
    c = np.zeros((0, 4), dtype=int)
    for i in range(talla):
        c = np.append(c, [pintar()], axis=0)
    return c

def mascara():
    global mig
    global gru
    global gvis
    if mig == -1:
        res = np.zeros(gru.size) == 0
    else:
        res = gru == mig
    res = np.where(gvis[gru], res, False)
    return res

def animacion(ani, nombre):
    global pos
    global col
    global gru
    global gvis
    global mig
    global escalaimg
    img = []
    # caida
    if ani[0]:
        retenerCambio()
        amig = mig
        for mov in ani[2:]:
            # inicio pre efectos
            pass
            # fin pre efectos
        sub = ani[1]
        for a in range(sub):
            for mov in ani[2:]:
                # inicio efectos
                #escalamiento(np.array([1, 1, ((sub - 1 - a) / sub)], dtype=float))
                pass
                # fin efectos
            if nombre == "":
                img.append(dibujar(False, True))
            else:
                agregarTXT(nombre, a)
        mig = amig
        retroceder()
    else:
        if nombre == "":
            img.append(dibujar(False, True))
        else:
            agregarTXT(nombre, 0)
    # escalar si se requiere
    if escalaimg != 1 and nombre == "":
        ori = img[0].get_size()
        wh = (int(ori[0] * escalaimg), int(ori[1] * escalaimg))
        for i in range(len(img)):
            img[i] = pg.transform.smoothscale(img[i], wh)
    return img

def guardarPNG(img, nombre, modo, caras):
    if len(img) == 1:
        pg.image.save(img[0], nombre + ".png")
    else:
        for i in range(len(img)):
            pg.image.save(img[i], nombre + "_" + str(i) + ".png")
        if modo != 3:
            fil = []
            for i in range(len(img)):
                fil.append(Image.open(nombre + "_" + str(i) + ".png"))
            www = fil[0].width
            hhh = fil[0].height
            if modo == 0:
                lienzo = Image.new("RGBA", (www * len(fil), hhh))
                for i in range(len(fil)):
                    lienzo.paste(fil[i], (www * i, 0))
                lienzo.save(nombre + "_strip" + str(len(fil)) + ".png")
            elif modo == 1:
                subimg = int(len(fil) / caras)
                i = 0
                for c in range(caras):
                    lienzo = Image.new("RGBA", (www * subimg, hhh))
                    for x in range(subimg):
                        lienzo.paste(fil[i], (www * x, 0))
                        i += 1
                    lienzo.save(nombre + "_c" + str(c) + "_strip" +
                                str(subimg) + ".png")
            elif modo == 2:
                subimg = int(len(fil) / caras)
                lienzo = Image.new("RGBA", (www * subimg, hhh * caras))
                i = 0
                for y in range(caras):
                    for x in range(subimg):
                        lienzo.paste(fil[i], (www * x, hhh * y))
                        i += 1
                lienzo.save(nombre + "_strip" + str(caras) + "x" +
                            str(subimg) + ".png")
            elif modo == 5:
                subimg = int(len(fil) / caras)
                if subimg == 1:
                    dur = caras
                else:
                    dur = subimg
                para, ok = inputVec(tab() + "duracion ciclo (ms) (vacio auto): ", 1)
                if ok:
                    dur = max(1, int(para[0] / dur))
                else:
                    dur = max(1, int(3200 / dur))
                fil[0].save(nombre + ".gif", format="GIF", append_images=fil[1:],
                            save_all=True, duration=dur, loop=0)
            for i in range(len(img)):
                os.remove(nombre + "_" + str(i) + ".png")

def rayoLuz(ini, fin, apos, aacol, agru, zona, extra, bias, plim):
    global cnfgluz
    pp = ini
    vel = fin - ini
    dis = magnitud(vel)
    if extra == 0:
        vel = (vel / max(1, dis)) * cnfgluz[0]
    else:
        vel = vel / max(1, dis)
        dis -= extra
        pp = pp + vel * extra
        vel = vel * cnfgluz[0]
    fuerza = cnfgluz[5]
    blanco = []
    fir = -1
    for i in range(int(np.ceil(dis / cnfgluz[0]))):
        if not (False in (pp >= plim[:3]) or False in (pp <= plim[3:6])):
            miz = enZona(pp, zona)
            for u in range(agru.size):
                if bias[u] and miz == agru[u]:
                    d = np.power(apos[u, :] - pp, 2.0).sum()
                    if d <= cnfgluz[1]:
                        bias[u] = False
                        if fuerza > 0:
                            if fir == -1:
                                fir = u
                            blanco.append([u, fuerza])
                            if d <= 36:
                                fuerza = max(0, fuerza - aacol[u, 3])
                            else:
                                fuerza = max(0, fuerza - aacol[u, 3] *
                                             max(0.1, 1 - (d / cnfgluz[1])))
                        break
        pp = pp + vel
    if fir != -1:
        bias[fir] = True
    return blanco, fuerza

def rayoColision(ini, fin, agru, zona, extra, bias, plim):
    global cnfgluz
    global pos
    pp = ini
    vel = fin - ini
    dis = magnitud(vel)
    if extra == 0:
        vel = (vel / max(1, dis)) * cnfgluz[0]
    else:
        vel = vel / max(1, dis)
        dis -= extra
        pp = pp + vel * extra
        vel = vel * cnfgluz[0]
    impac = -1
    for i in range(int(np.ceil(dis / cnfgluz[0]))):
        if not (False in (pp >= plim[:3]) or False in (pp <= plim[3:6])):
            miz = enZona(pp, zona)
            for u in range(agru.size):
                if bias[u] and miz == agru[u]:
                    d = np.power(pos[u, :] - pp, 2.0).sum()
                    if d <= cnfgluz[6]:
                        bias[u] = False
                        if impac == -1:
                            impac = u
                        break
        pp = pp + vel
    if impac != -1:
        bias[impac] = True
    return impac

def rayoBasico(ini, fin, plim):
    global cnfgluz
    global pos
    global gru
    pp = ini
    vel = fin - ini
    dis = magnitud(vel)
    vel = (vel / max(1, dis)) * cnfgluz[0]
    ggg = mascara()
    impac = -1
    for i in range(int(np.ceil(dis / cnfgluz[0]))):
        if not (False in (pp >= plim[:3]) or False in (pp <= plim[3:6])):
            for u in range(gru.size):
                if ggg[u]:
                    d = np.power(pos[u, :] - pp, 2.0).sum()
                    if d <= cnfgluz[6]:
                        if impac == -1:
                            impac = u
                        break
        if impac != -1:
            break
        pp = pp + vel
    return impac

def zonificar():
    global pos
    global col
    global gru
    global gvis
    global cnfgluz
    p = np.zeros((0, 3), dtype=float)
    c = np.zeros((0, 4), dtype=int)
    g = np.zeros(0, dtype=int)
    plim = np.append(np.min(pos, axis=0), np.max(pos, axis=0))
    plim = plim + np.array([-6, -6, -6, 6, 6, 6])
    zona = []
    pl = np.array(plim, dtype=int)
    for x in range(pl[0], pl[3] + 1, cnfgluz[3]):
        for y in range(pl[1], pl[4] + 1, cnfgluz[3]):
            for z in range(pl[2], pl[5] + 1, cnfgluz[3]):
                zona.append([x, y, z])
    zona = np.array(zona)
    gvv = gvis[gru]
    for u in range(gru.size):
        if gvv[u]:
            miz = enZona(pos[u, :], zona)
            p = np.append(p, [pos[u, :]], axis=0)
            c = np.append(c, [col[u, :]], axis=0)
            g = np.append(g, miz)
    return p, c, g, zona, plim

def zonificarGeneral():
    global pos
    global gru
    global cnfgluz
    g = gru.copy()
    plim = np.append(np.min(pos, axis=0), np.max(pos, axis=0))
    plim = plim + np.array([-6, -6, -6, 6, 6, 6])
    zona = []
    pl = np.array(plim, dtype=int)
    for x in range(pl[0], pl[3] + 1, cnfgluz[3]):
        for y in range(pl[1], pl[4] + 1, cnfgluz[3]):
            for z in range(pl[2], pl[5] + 1, cnfgluz[3]):
                zona.append([x, y, z])
    zona = np.array(zona)
    for u in range(gru.size):
        g[u] = enZona(pos[u, :], zona)
    return g, zona, plim

def enZona(des, zona):
    tot = np.sum(np.power(des - zona, 2.0), axis=1)
    # return np.random.randint(0, 10, 1)[0]
    # return 0
    return np.argmin(tot)

def giroInt(npos, gra):
    if gra != 0:
        if npos.shape[0] > 0:
            dis = np.sqrt(np.sum(np.power(npos[:, :2], 2.0), axis=1))
            www = dis == 0
            ang = np.where(www, 0, np.arccos(npos[:, 0] / np.where(www, 1, dis)))
            ang = np.where(npos[:, 1] > 0, ang, -ang)
            ang = ang + np.deg2rad(gra)
            npos[:, 0] = dis * np.cos(ang)
            npos[:, 1] = dis * np.sin(ang)
    return npos

def giroAbs(npos):
    global flags
    global giro
    if flags[2]:
        return giroInt(npos, giro)
    else:
        return npos

# funciones de administracion:

def retroceder():
    global pos
    global col
    global gru
    global giro
    global gvis
    global memoria
    if len(memoria) > 0:
        m = memoria.pop(-1)
        giro = m[0]
        pos = m[1]
        col = m[2]
        gru = m[3]
        gvis = m[4]
        verificarGrupos()

def visibleGrupo(g):
    global gvis
    global mig
    if g == -1:
        if np.array_equal(gvis, np.zeros(gvis.size, dtype=int) == 0):
            gvis = np.zeros(gvis.size, dtype=int) == 1
        else:
            gvis = np.zeros(gvis.size, dtype=int) == 0
    elif g < gvis.size:
        gvis[g] = not gvis[g]

def exportarPNG(nombre, ang, ani, modo):
    global flags
    nombre = nombre.replace(".png", "").replace(".txt", "").replace(".gif", "")
    nombre = "img" if len(nombre) == 0 else nombre
    if modo == 4:
        guardarTXT(nombre, True)
    # obtener iterativamente las diferentes vistas
    agiro = giraCentro() if flags[2] else 0
    img = []
    for r in range(ang):
        img = img + animacion(ani, (nombre if modo == 4 else ""))
        giraTodo(360 / ang)
    giraTodo(agiro)
    if modo != 4 and modo != 6:
        guardarPNG(img, nombre, modo, ang)
    if flags[0]:
        dibujar()

def informacion():
    global giro
    global gru
    global gvis
    global ecol
    global contorno
    global escalaimg
    global cen
    print("***Informacion***")
    print(tab() + "voxels: " + str(gru.size))
    print(tab() + "grupos: " + str(gvis.size))
    if gvis.size > 0:
        print(tab() + "visibles: " + str(int(np.where(gvis, 1, 0).mean() * 100)) + "%")
    else:
        print(tab() + "visibles: 0%")
    print(tab() + "texturas: " + str(len(ecol)))
    print(tab() + "giro: " + str(giro) + "°")
    print(tab() + "contorno: " + losContornos()[contorno])
    print(tab() + "escala PNG: " + str(int(escalaimg * 100)) + "%")
    print(tab() + "centro en: " + str(int(cen[0] * escalaimg)) + "x" +
          str(int(cen[1] * escalaimg)) + " px")

def lasBanderas():
    global flags
    global cnfgluz
    print("***Configuracion***")
    print(tab() + "autodraw: " + ("On" if flags[0] else "Off"))
    print(tab() + "dibujar planos: " + ("On" if flags[5] else "Off"))
    print(tab() + "origen absoluto: " + ("On" if flags[2] else "Off"))
    print(tab() + "render luz: " + ("On" if flags[1] else "Off"))
    print(tab() + "camara en picada: " + ("On" if flags[4] else "Off"))
    print(tab() + "ver fondos: " + ("On" if flags[6] else "Off"))
    print(tab() + "tipo de luz: " + ("Foco" if flags[3] else "Sol"))
    print(tab() + "luz ambiente: " + str(int(cnfgluz[4] * 100)) + "%")
    print(tab() + "fuerza luz: " + str(int((cnfgluz[5] / 255) * 100)) + "%")

def guardarTXT(nombre, completo, recordar=False):
    global pos
    global col
    global gru
    global ecol
    global cnfgluz
    global gvis
    global flags
    global contorno
    global luz
    global escalaimg
    global mat
    global archul
    nombre = nombre.replace(".txt", "")
    nombre = (archul if archul != "" else "vox") if nombre == "" else nombre
    nombre = nombre + ".txt"
    f = open(nombre, "w")
    f.write("OmiVoxel " + version() + " (" + str(mat[0]) + "x" + str(mat[1]) +
            " px) (" + dt.now().strftime("%d/%m/%Y %H:%M:%S") + ")\n")
    f.write("$Texturas (nombre,r1,g1,b1,a1,r2,g2,b2,a2,r3,g3,b3,a3)$\n")
    for c in ecol:
        f.write(c[0] + ",")
        txt = ""
        for i in range(3):
            for j in range(4):
                txt += str(c[1][i][j]) + ","
        f.write(txt[:-1] + "\n")
    f.write("$Voxels (x,y,z,r,g,b,a,grupo)$\n")
    agiro = giraCentro()
    ggg = mascara()
    for u in range(gru.size):
        if ggg[u] or completo:
            for i in range(3):
                f.write(str(pos[u, i]) + ",")
            for i in range(4):
                f.write(str(col[u, i]) + ",")
            f.write(str(gru[u]) + "\n")
    f.write("$Config (luzambiente,luzfuerza,contorno,escalapng,giro)\n" +
            "        (g0vis,g1vis,g2vis,...)\n" +
            "        (autodraw,renderluz,absoluto,focal,picada,dibuplanos,verfondos)\n" +
            "        (luz_x,luz_y,luz_z)$\n")
    f.write(str(cnfgluz[4]) + ",")
    f.write(str(cnfgluz[5]) + ",")
    f.write(str(contorno) + ",")
    f.write(str(escalaimg) + ",")
    f.write(str(agiro) + "\n")
    txt = ""
    for v in gvis:
        txt += ("1" if v else "0") + ","
    f.write((txt[:-1] if txt[:-1] != "" else "0") + "\n")
    txt = ""
    for v in flags:
        txt += ("1" if v else "0") + ","
    f.write(txt[:-1] + "\n")
    f.write(str(luz[0]) + "," + str(luz[1]) + "," + str(luz[2]) + "\n")
    f.write("$AnimaFrames (#0 voxels, #1 voxels, #2 voxels, ...)$\n")
    f.close()
    if recordar:
        archul = nombre.replace(".txt", "")
    giraTodo(agiro)

def abrirTXT(nombre, textu, voxel, config, animm, recordar=False):
    global gru
    global ecol
    global cnfgluz
    global contorno
    global escalaimg
    global gvis
    global flags
    global luz
    global archul
    nombre = nombre.replace(".txt", "") + ".txt"
    if os.path.exists(nombre):
        f = open(nombre, "r")
        txt = f.read()
        f.close()
        if recordar:
            archul = nombre.replace(".txt", "")
        # 0-titulo, 1-texturainfo, 2-texturas, 3-voxelinfo,
        # 4-voxels, 5-configinfo, 6-configs
        txt = txt.split("$")
        if textu:
            data = txt[2][1:-1].split("\n")
            for d in data:
                if d != "":
                    v = d.split(",")
                    c1 = np.array([int(v[1]), int(v[2]), int(v[3]), int(v[4])])
                    c2 = np.array([int(v[5]), int(v[6]), int(v[7]), int(v[8])])
                    c3 = np.array([int(v[9]), int(v[10]), int(v[11]), int(v[12])])
                    ecol.append([v[0], [c1, c2, c3]])
            unicaTextura()
        if voxel:
            data = txt[4][1:-1].split("\n")
            p = np.zeros((0, 3), dtype=float)
            c = np.zeros((0, 4), dtype=int)
            g = np.zeros(0, dtype=int)
            for d in data:
                if d != "":
                    v = d.split(",")
                    p = np.append(p, np.array([[float(v[0]), float(v[1]),
                                               float(v[2])]]), axis=0)
                    c = np.append(c, np.array([[int(v[3]), int(v[4]),
                                               int(v[5]), int(v[6])]]), axis=0)
                    g = np.append(g, int(v[7]))
            if g.size > 0:
                retenerCambio()
                g = g - g.min()
                if gru.size > 0:
                    m = gru.max()
                    g = g + (m + 1)
                agregar(p, c, g)
        if config:
            data = txt[6][1:-1].split("\n")
            tip = 0
            agiro = 0
            for d in data:
                if d != "":
                    v = d.split(",")
                    if tip == 0:
                        cnfgluz[4] = float(v[0])
                        cnfgluz[5] = int(v[1])
                        contorno = int(v[2])
                        escalaimg = float(v[3])
                        agiro = float(v[4])
                    elif tip == 1:
                        gvis = np.zeros(0, dtype=int) == 0
                        for vv in v:
                            gvis = np.append(gvis, (True if vv == "1" else False))
                    elif tip == 2:
                        for f in range(len(flags)):
                            flags[f] = (True if v[f] == "1" else False)
                    elif tip == 3:
                        luz = np.array([float(v[0]), float(v[1]), float(v[2])])
                    tip += 1
            verificarGrupos()
            giraCentro()
            giraTodo(agiro)
        if animm:
            pass
    elif nombre != "config.txt":
        print(tab() + "!!!")

def agregarTXT(nombre, ind):
    global pos
    global col
    global gru
    global gvis
    global archul
    nombre = nombre.replace(".txt", "")
    nombre = (archul if archul != "" else "vox") if nombre == "" else nombre
    nombre = nombre + ".txt"
    if os.path.exists(nombre):
        f = open(nombre, "a")
        f.write("#" + str(ind) + "\n")
        gvv = gvis[gru]
        for u in range(gru.size):
            if gvv[u]:
                for i in range(3):
                    f.write(str(pos[u, i]) + ",")
                for i in range(4):
                    f.write(str(col[u, i]) + ",")
                f.write(str(gru[u]) + "\n")
        f.close()

def acercaDe():
    global mat
    global cen
    global cuadrito
    print("***Acerca De***")
    print(version() + " OmiVoxel por Omarsaurio 2020")
    print("Software para modelado 2.5D por codigo e inspirado")
    print("en el voxel (aunque no lo es), puede exportar")
    print("sprites listos para uso en juegos isometricos,")
    print("da una estetica muy particulada.")
    print("- voxel 6 px radio")
    print("- lienzo de " + str(mat[0]) + "x" + str(mat[1]) + " px")
    print("- volumen de {}x{}x{} px".format(str(mat[0]), str(mat[0]),
                                       str(mat[1] - mat[0])))
    print("- fondos de " + str(mat[0]) + "x" + str(mat[0]) + " px y 2x " +
          str(mat[0]) + "x" + str(int(mat[1] - mat[0] / 4)) + " px")
    print("  con centro en {}x{} px y 2x {}x{} px".format(int(cen[0]), int(cen[0]),
                                                     int(cen[0]), int(cen[1])))
    print("- centro en " + str(int(cen[0])) + "x" +
          str(int(cen[1])) + " px")
    print("- cuadricula de " + str(cuadrito) + " px")

def sintaxis():
    print("***Sintaxis***")
    print("- al digitar un valor x,y,z puedes escribir en su lugar:")
    print("  ori, para 0,0,0")
    print("  masa, para el centro de masa de un grupo dado")
    print("  base, para el centro de masa con z menor del grupo dado")
    print("  tierra, para el centro de masa con z en 0 del grupo dado")
    print("    por ej: x,y,z,r,h puede escribirse masa,r,h (r,h valores)")
    print("  rf, random -1 a 1, rp, random 0 a 1")
    print("  ru, random -cuadricula o 0 o cuadricula")
    print("  rs, random 0 a lienzo w / 2")
    print("  azar, random,random,random de los limites del lienzo")
    print("  rand, random,random,random de limites inferiores al lienzo")
    print("  u, para unidad de cuadricula, por ej: 3.5u,-u,15")
    print("- al digitar un color puede omitirse el alfa, por defecto 255,")
    print("  si el c2 se deja vacio, sera igual a c1, mismo para c3->c2")
    print("- el valor eje hace referencia a 0->x 1->y 2->z")
    print("- el valor porc refiere a un porcentaje entre 0 y 1")
    print("- el valor ang es un angulo en grados")
    print("- para elegir grupo, -1 global, vacio sera el actual")
    print("- al ingresar varios puntos, use x para eliminar anterior")
    print("- al ingresar varios puntos, solo x,y hara z=0")
    print("- booleanos (s/n) tiene por defecto a la mayuscula, ej: s/N")

def losEfectos():
    print("***Efectos***")
    print("-   Transformacion:")
    print("mover, rotar, escalar, demoler, limitar, oscila mover,")
    print("oscila rotar, oscila escalar, respirar, inflar, balancear")
    print("-   Destruccion:")
    print("(todos llevan borra/b antes de...)")
    print("bajotierra, colision, cruzados, esfera, cilindro, cubo,")
    print("azar, cercano, limite")
    print("-   Dibujado:")
    print("visible, brocha esfera, brocha caja, brocha cilindro,")
    print("brocha azar, gira luz, mueve luz, ")

def laAyuda():
    print("***Comandos***")
    print(tab() + "Administracion:")
    print("salir, atras, z, grupo, ver, nuevo, visible, exportar,")
    print("info, guardar, abrir, acercade, ayuda, salvar, s, sintaxis,")
    print("modelo, cargar, guardar pieza, banderas, escalapng")
    print(tab() + "Animacion:")
    print("efectos, crear anima, ver anima, borra anima")
    print(tab() + "Transformacion:")
    print("girar, centrar, d, a, posicion, rotar, espejo, revolucion,")
    print("mezclar, duplicar, mover, escalar, masa, estruir, limitar,")
    print("tierra, sim azar, sim velocidad, sim gravedad, sim colision,")
    print("sim foco, sim enjambre, sim demoler, sim torcion, sim tornado,")
    print("invertir, anomalias, clon linea, clon aro")
    print(tab() + "Destruccion:")
    print("(todos llevan borra/b antes de...)")
    print("bajotierra, grupo, colision, cruzados, esfera, cilindro,")
    print("cubo, azar, cercano, limite, luz, taladro")
    print(tab() + "Creacion:")
    print("(todos llevan crear/c antes de..., luego solido...)")
    print("punto, aro, cilindro, esfera, cono, demo, palo, silueta,")
    print("marco, cuadro, caja, piramide, circulo, rayo, arbol, rueda,")
    print("azar esfera, azar cilindro, relleno, mancha, poligono,")
    print("paredes, revolucion, sombra, obra, techo, rampa, pelo,")
    print("monigote, loco, maniqui")
    print(tab() + "Dibujado:")
    print("color, crear textura, ver texturas, borra textura,")
    print("textura, pintar, render, galeria, contorno, autodraw,")
    print("renderluz, tipoluz, brocha esfera, brocha caja, fondos,")
    print("brocha cilindro, brocha azar, fuerza luz, picada,")
    print("posicion luz, luz defecto, dibuplanos, verfondos,")
    print("filtro, poner alfa, escalar alfa, pintar luz, color azar,")
    print("efecto color, pintar textura, p textura, pintar sombra")

# funciones de transformacion:

def luzDefecto():
    global mat
    global luz
    global giro
    luz = np.array([-mat[0] / 4, mat[0] / 4, mat[1] - mat[0]], dtype=float)
    giraLuz(giro)

def giraTodo(gra):
    global pos
    global giro
    if gra != 0:
        pos = giroInt(pos, gra)
        giraLuz(gra)
        giro += gra
        if giro >= 360:
            giro -= 360
        elif giro < 0:
            giro += 360

def giraCentro():
    global giro
    agiro = giro
    giraTodo(-agiro)
    return agiro

def giraLuz(gra):
    global luz
    if gra != 0:
        dis = magnitud(luz[:2])
        if dis != 0:
            ang = np.arccos(luz[0] / dis)
            ang = ang if luz[1] > 0 else -ang
            ang = ang + np.deg2rad(gra)
            luz[0] = dis * np.cos(ang)
            luz[1] = dis * np.sin(ang)

def trasladaLuz(des):
    global luz
    global flags
    global giro
    luz = des
    if flags[2]:
        giraLuz(giro)

def eliminarBajotierra():
    global pos
    global col
    global gru
    global mig
    if gru.size > 0:
        ggg = mascara()
        for u in range(gru.size - 1, -1, -1):
            if pos[u, 2] < 0 and ggg[u]:
                pos = np.delete(pos, u, axis=0)
                col = np.delete(col, u, axis=0)
                gru = np.delete(gru, u)
        verificarGrupos()

def eliminarGrupo():
    global pos
    global col
    global gru
    global mig
    global gvis
    if gru.size > 0:
        if mig == -1 or gvis.size == 1:
            pos = np.zeros((0, 3), dtype=float)
            col = np.zeros((0, 4), dtype=int)
            gru = np.zeros(0, dtype=int)
        else:
            ggg = mascara()
            for u in range(gru.size - 1, -1, -1):
                if ggg[u]:
                    pos = np.delete(pos, u, axis=0)
                    col = np.delete(col, u, axis=0)
                    gru = np.delete(gru, u)
        verificarGrupos()

def mezclarGrupos(g):
    global gru
    global mig
    if gru.size > 0:
        if mig != -1:
            for u in range(gru.size):
                if g == gru[u] or g == -1:
                    gru[u] = mig
            verificarGrupos()
        else:
            print(tab() + "no puede unirse a -1")

def duplicarGrupo():
    global pos
    global col
    global gru
    global mig
    global flags
    if gru.size > 0:
        agiro = giraCentro() if flags[2] else 0
        p = np.zeros((0, 3), dtype=float)
        c = np.zeros((0, 4), dtype=int)
        ggg = mascara()
        for u in range(gru.size):
            if ggg[u]:
                p = np.append(p, [pos[u, :]], axis=0)
                c = np.append(c, [col[u, :]], axis=0)
        g = np.zeros(p.shape[0], dtype=int) + grupoVacio()
        agregar(p, c, g)
        giraTodo(agiro)

def posicion(des, newpos):
    global pos
    global gru
    global flags
    if gru.size > 0:
        agiro = giraCentro() if flags[2] else 0
        pos = np.where(np.reshape(mascara(), (-1, 1)), pos + (newpos - des), pos)
        giraTodo(agiro)

def traslacion(des):
    global pos
    global gru
    global flags
    if gru.size > 0:
        agiro = giraCentro() if flags[2] else 0
        pos = np.where(np.reshape(mascara(), (-1, 1)), pos + des, pos)
        giraTodo(agiro)

def escalamiento(des, mul):
    global pos
    global gru
    global flags
    if gru.size > 0:
        agiro = giraCentro() if flags[2] else 0
        pos = np.where(np.reshape(mascara(), (-1, 1)),
                       ((pos - des) * mul) + des, pos)
        giraTodo(agiro)

def masaCentro(show):
    global pos
    global gru
    global flags
    if gru.size > 0:
        agiro = giraCentro() if flags[2] else 0
        ggg = mascara()
        des = np.sum(np.where(np.reshape(ggg, (-1, 1)), pos, 0), axis=0)
        mas = np.where(ggg, 1, 0).sum()
        des = des / max(1, mas)
        base = np.where(ggg, pos[:, 2], des[2]).min()
        if show:
            print(tab() + "centro: {},{},{}".format(
                int(des[0]), int(des[1]), int(des[2])))
            print(tab() + "base: " + str(int(base)))
            print(tab() + "masa: " + str(mas) + "u")
        giraTodo(agiro)
        return des, base, mas
    else:
        return np.zeros(3, dtype=float), 0, 0

def eliminarColision(g, borde=20):
    global gru
    global pos
    global col
    global gvis
    if gru.size > 0:
        ggg = mascara()
        bias = np.zeros(gru.size, dtype=int) == 0
        cola = np.zeros(gru.size, dtype=int) == 1
        des, base, mas = masaCentro(False)
        dep = np.argsort(np.sum(np.power(pos - des, 2.0), axis=1))
        for u in dep:
            if ggg[u] and bias[u]:
                bias[u] = False
                for v in range(gru.size):
                    if (gru[v] == g or g == -1) and bias[v] and gvis[gru[v]]:
                        d = np.power(pos[u, :] - pos[v, :], 2.0).sum()
                        if d <= borde:
                            bias[v] = False
                            cola[u] = True
                            break
        for u in range(gru.size - 1, -1, -1):
            if cola[u]:
                pos = np.delete(pos, u, axis=0)
                col = np.delete(col, u, axis=0)
                gru = np.delete(gru, u)
        verificarGrupos()

def rotacion(des, gra):
    global pos
    global gru
    global mig
    global flags
    if gru.size > 0:
        agiro = giraCentro() if flags[2] else 0
        ggg = mascara()
        pos = np.where(np.reshape(ggg, (-1, 1)), pos - des, pos)
        if gra[0] != 0:
            dis = np.sqrt(np.sum(np.power(pos[:, 1:3], 2.0), axis=1))
            www = dis == 0
            ang = np.where(www, 0, np.arccos(pos[:, 1] / np.where(www, 1, dis)))
            ang = np.where(pos[:, 2] > 0, ang, -ang)
            ang = ang + np.deg2rad(gra[0])
            pos[:, 1] = np.where(ggg, dis * np.cos(ang), pos[:, 1])
            pos[:, 2] = np.where(ggg, dis * np.sin(ang), pos[:, 2])
        if gra[1] != 0:
            dis = np.sqrt(np.sum(np.power(pos[:, 0:3:2], 2.0), axis=1))
            www = dis == 0
            ang = np.where(www, 0, np.arccos(pos[:, 0] / np.where(www, 1, dis)))
            ang = np.where(pos[:, 2] > 0, ang, -ang)
            ang = ang + np.deg2rad(gra[1])
            pos[:, 0] = np.where(ggg, dis * np.cos(ang), pos[:, 0])
            pos[:, 2] = np.where(ggg, dis * np.sin(ang), pos[:, 2])
        if gra[2] != 0:
            dis = np.sqrt(np.sum(np.power(pos[:, :2], 2.0), axis=1))
            www = dis == 0
            ang = np.where(www, 0, np.arccos(pos[:, 0] / np.where(www, 1, dis)))
            ang = np.where(pos[:, 1] > 0, ang, -ang)
            ang = ang + np.deg2rad(gra[2])
            pos[:, 0] = np.where(ggg, dis * np.cos(ang), pos[:, 0])
            pos[:, 1] = np.where(ggg, dis * np.sin(ang), pos[:, 1])
        pos = np.where(np.reshape(ggg, (-1, 1)), pos + des, pos)
        giraTodo(agiro)

def espejo(ejex, ejey):
    global pos
    global gru
    global col
    global flags
    if gru.size > 0:
        agiro = giraCentro() if flags[2] else 0
        ggg = mascara()
        for u in range(gru.size - 1, -1, -1):
            if ((pos[u, 0] < 0 and ejex) or (pos[u, 1] < 0 and ejey)) and ggg[u]:
                pos = np.delete(pos, u, axis=0)
                col = np.delete(col, u, axis=0)
                gru = np.delete(gru, u)
        p = np.zeros((0, 3), dtype=float)
        c = np.zeros((0, 4), dtype=int)
        g = np.zeros(0, dtype=int)
        ggg = mascara()
        if ejex and not ejey:
            for u in range(gru.size):
                if ggg[u]:
                    p = np.append(p, [pos[u, :] * np.array([-1, 1, 1])], axis=0)
                    c = np.append(c, [col[u, :]], axis=0)
                    g = np.append(g, gru[u])
        elif ejey and not ejex:
            for u in range(gru.size):
                if ggg[u]:
                    p = np.append(p, [pos[u, :] * np.array([1, -1, 1])], axis=0)
                    c = np.append(c, [col[u, :]], axis=0)
                    g = np.append(g, gru[u])
        elif ejex and ejey:
            for u in range(gru.size):
                if ggg[u]:
                    p = np.append(p, [pos[u, :] * np.array([-1, 1, 1])], axis=0)
                    c = np.append(c, [col[u, :]], axis=0)
                    g = np.append(g, gru[u])
                    p = np.append(p, [pos[u, :] * np.array([1, -1, 1])], axis=0)
                    c = np.append(c, [col[u, :]], axis=0)
                    g = np.append(g, gru[u])
                    p = np.append(p, [pos[u, :] * np.array([-1, -1, 1])], axis=0)
                    c = np.append(c, [col[u, :]], axis=0)
                    g = np.append(g, gru[u])
        agregar(p, c, g)
        giraTodo(agiro)

def revolucion():
    global pos
    global gru
    global col
    global mig
    global acol
    global flags
    if gru.size > 0 and mig != -1:
        agiro = giraCentro() if flags[2] else 0
        ggg = mascara()
        aacol = acol.copy()
        for u in range(gru.size - 1, -1, -1):
            if ggg[u]:
                if pos[u, 0] >= 0 and pos[u, 1] == 0:
                    acol = [col[u, :], col[u, :], col[u, :]]
                    crearAro(np.array([0, 0, pos[u, 2]]), pos[u, 0], 2)
        acol = aacol
        for u in range(ggg.size - 1, -1, -1):
            if ggg[u]:
                pos = np.delete(pos, u, axis=0)
                col = np.delete(col, u, axis=0)
                gru = np.delete(gru, u)
        giraTodo(agiro)
        verificarGrupos()

def estrucion(alt, eje):
    global pos
    global gru
    global col
    global mig
    global acol
    global flags
    if gru.size > 0 and mig != -1:
        agiro = giraCentro() if flags[2] else 0
        ggg = mascara()
        aacol = acol.copy()
        for u in range(gru.size - 1, -1, -1):
            if ggg[u]:
                acol = [col[u, :], col[u, :], col[u, :]]
                crearCilindro(pos[u, :], 0, alt, eje)
        acol = aacol
        for u in range(ggg.size - 1, -1, -1):
            if ggg[u]:
                pos = np.delete(pos, u, axis=0)
                col = np.delete(col, u, axis=0)
                gru = np.delete(gru, u)
        giraTodo(agiro)
        verificarGrupos()

def clonAro(des, gra):
    global pos
    global gru
    global col
    global flags
    if gru.size > 0:
        agiro = giraCentro() if flags[2] else 0
        p = np.zeros((0, 3), dtype=float)
        c = np.zeros((0, 4), dtype=int)
        g = np.zeros(0, dtype=int)
        ggg = mascara()
        for r in np.arange(gra, 360, gra):
            for u in range(gru.size):
                if ggg[u]:
                    p = np.append(p, [pos[u, :]], axis=0)
                    c = np.append(c, [col[u, :]], axis=0)
                    g = np.append(g, gru[u])
            p = giroInt(p - des, gra)
            p = p + des
        agregar(p, c, g)
        giraTodo(agiro)

def clonLinea(linea, paso):
    global pos
    global gru
    global col
    global flags
    if gru.size > 0:
        agiro = giraCentro() if flags[2] else 0
        p = np.zeros((0, 3), dtype=float)
        c = np.zeros((0, 4), dtype=int)
        g = np.zeros(0, dtype=int)
        ggg = mascara()
        long = magnitud(linea)
        dd = linea / long
        for h in np.arange(paso, long, paso):
            for u in range(gru.size):
                if ggg[u]:
                    p = np.append(p, [pos[u, :] + dd * h], axis=0)
                    c = np.append(c, [col[u, :]], axis=0)
                    g = np.append(g, gru[u])
        agregar(p, c, g)
        giraTodo(agiro)

def eliminarEsfera(des, rad, inv=False):
    global gru
    global pos
    global col
    global flags
    if gru.size > 0:
        agiro = giraCentro() if flags[2] else 0
        ggg = mascara()
        dmin = np.power(rad, 2.0)
        for u in range(gru.size - 1, -1, -1):
            if ggg[u]:
                d = np.power(pos[u, :] - des, 2.0).sum()
                if (d <= dmin) != inv:
                    pos = np.delete(pos, u, axis=0)
                    col = np.delete(col, u, axis=0)
                    gru = np.delete(gru, u)
        verificarGrupos()
        giraTodo(agiro)

def eliminarCaja(des1, des2, inv=False):
    global gru
    global pos
    global col
    global flags
    if gru.size > 0:
        agiro = giraCentro() if flags[2] else 0
        ggg = mascara()
        for u in range(gru.size - 1, -1, -1):
            if ggg[u]:
                if not (False in (pos[u, :] >= des1) or
                        False in (pos[u, :] <= des1 + des2)) != inv:
                    pos = np.delete(pos, u, axis=0)
                    col = np.delete(col, u, axis=0)
                    gru = np.delete(gru, u)
        verificarGrupos()
        giraTodo(agiro)

def eliminarCilindro(des, rad, alt, eje, inv=False):
    global gru
    global pos
    global col
    global flags
    if gru.size > 0:
        agiro = giraCentro() if flags[2] else 0
        ggg = mascara()
        dmin = np.power(rad, 2.0)
        if eje == 0:
            for u in range(gru.size - 1, -1, -1):
                if ggg[u]:
                    bor = False
                    if inv:
                        if pos[u, 0] < des[0] or pos[u, 0] > des[0] + alt:
                            bor = True
                        else:
                            d = np.power(pos[u, 1:3] - des[1:3], 2.0).sum()
                            if d > dmin:
                                bor = True
                    else:
                        if pos[u, 0] >= des[0] and pos[u, 0] <= des[0] + alt:
                            d = np.power(pos[u, 1:3] - des[1:3], 2.0).sum()
                            if (d <= dmin) != inv:
                                bor = True
                    if bor:
                        pos = np.delete(pos, u, axis=0)
                        col = np.delete(col, u, axis=0)
                        gru = np.delete(gru, u)
        elif eje == 1:
            for u in range(gru.size - 1, -1, -1):
                if ggg[u]:
                    bor = False
                    if inv:
                        if pos[u, 1] < des[1] and pos[u, 1] > des[1] + alt:
                            bor = True
                        else:
                            d = np.power(pos[u, 0:3:2] - des[0:3:2], 2.0).sum()
                            if d > dmin:
                                bor = True
                    else:
                        if pos[u, 1] >= des[1] and pos[u, 1] <= des[1] + alt:
                            d = np.power(pos[u, 0:3:2] - des[0:3:2], 2.0).sum()
                            if d <= dmin:
                                bor = True
                    if bor:
                        pos = np.delete(pos, u, axis=0)
                        col = np.delete(col, u, axis=0)
                        gru = np.delete(gru, u)
        else:
            for u in range(gru.size - 1, -1, -1):
                if ggg[u]:
                    bor = False
                    if inv:
                        if pos[u, 2] < des[2] and pos[u, 2] > des[2] + alt:
                            bor = True
                        else:
                            d = np.power(pos[u, :2] - des[:2], 2.0).sum()
                            if d > dmin:
                                bor = True
                    else:
                        if pos[u, 2] >= des[2] and pos[u, 2] <= des[2] + alt:
                            d = np.power(pos[u, :2] - des[:2], 2.0).sum()
                            if d <= dmin:
                                bor = True
                    if bor:
                        pos = np.delete(pos, u, axis=0)
                        col = np.delete(col, u, axis=0)
                        gru = np.delete(gru, u)
        verificarGrupos()
        giraTodo(agiro)

def eliminarAzar(porc):
    global gru
    global pos
    global col
    if gru.size > 0:
        ggg = mascara()
        des, base, mas = masaCentro(False)
        repit = int(np.floor(mas * porc))
        for r in range(repit):
            while True:
                u = np.random.randint(0, gru.size, 1)[0]
                if ggg[u]:
                    pos = np.delete(pos, u, axis=0)
                    col = np.delete(col, u, axis=0)
                    gru = np.delete(gru, u)
                    break
        verificarGrupos()

def eliminarLimites():
    global pos
    global col
    global gru
    global mat
    if gru.size > 0:
        agiro = giraCentro() if flags[2] else 0
        ggg = mascara()
        minf = [-mat[0] / 2, -mat[0] / 2, 0]
        msup = [mat[0] / 2, mat[0] / 2, mat[1] - mat[0] / 2]
        linf = np.sum(pos < np.array(minf), axis=1) > 0
        lsup = np.sum(pos > np.array(msup), axis=1) > 0
        for u in range(gru.size - 1, -1, -1):
            if ggg[u]:
                if linf[u] or lsup[u]:
                    pos = np.delete(pos, u, axis=0)
                    col = np.delete(col, u, axis=0)
                    gru = np.delete(gru, u)
        verificarGrupos()
        giraTodo(agiro)

def limitar(soloSuelo=False):
    global pos
    global mat
    if gru.size > 0:
        if soloSuelo:
            pos = np.where(np.reshape(mascara(), (-1, 1)),
                           np.where(np.reshape(pos[:, 2] < 0, (-1, 1)),
                           pos * np.array([1, 1, 0]), pos), pos)
        else:
            agiro = giraCentro() if flags[2] else 0
            minf = [-mat[0] / 2, -mat[0] / 2, 0]
            msup = [mat[0] / 2, mat[0] / 2, mat[1] - mat[0] / 2]
            pos = np.where(np.reshape(mascara(), (-1, 1)),
                           pos.clip(minf, msup), pos)
            giraTodo(agiro)

def eliminarLuz():
    global luz
    global pos
    global col
    global gru
    global cnfgluz
    global mat
    global flags
    if gru.size > 0:
        agiro = giraCentro() if flags[2] else 0
        ggg = mascara()
        agru, zona, plim = zonificarGeneral()
        colis = np.zeros(agru.size, dtype=int) == 1
        bias = ggg.copy()
        if flags[3]:
            lux = luz
            extra = 0
        else:
            lux = (luz / magnitud(luz)) * cnfgluz[2]
            extra = cnfgluz[2] - magnitud(np.array([mat[0], mat[0], mat[1]]))
        dep = np.argsort(np.sum(np.power(pos - lux, 2.0), axis=1))
        for d in range(dep.size - 1, -1, -1):
            dd = dep[d]
            if bias[dd] and not colis[dd]:
                impac = rayoColision(lux, pos[dd, :], agru, zona, extra, bias, plim)
                if impac == -1:
                    colis[dd] = True
                else:
                    colis[impac] = True
        for u in range(gru.size - 1, -1, -1):
            if colis[u]:
                pos = np.delete(pos, u, axis=0)
                col = np.delete(col, u, axis=0)
                gru = np.delete(gru, u)
        verificarGrupos()
        giraTodo(agiro)

def eliminarRayo(ini, fin, terminar, rad):
    global gru
    global pos
    if gru.size > 0:
        agiro = giraCentro() if flags[2] else 0
        while True:
            if gru.size > 0:
                plim = np.append(np.min(pos, axis=0), np.max(pos, axis=0))
                plim = plim + np.array([-6, -6, -6, 6, 6, 6])
                impac = rayoBasico(ini, fin, plim)
                if impac != -1:
                    eliminarEsfera(pos[impac, :], rad)
                    if not terminar:
                        break
                else:
                    break
            else:
                break
        giraTodo(agiro)

def particulasAzar():
    global pos
    global gru
    if gru.size > 0:
        des = np.random.random_sample((gru.size, 3)) * 2.0 - 1.0
        des = des / np.reshape(np.sqrt(np.sum(np.power(des, 2.0), axis=1)), (-1, 1))
        pos = np.where(np.reshape(mascara(), (-1, 1)), pos + des * 12.0, pos)

def particulasVelcidad(restart=False):
    global pos
    global gru
    global vel
    global mig
    if gru.size > 0:
        des = np.random.random_sample((gru.size, 3)) * 2.0 - 1.0
        des = des / np.reshape(np.sqrt(np.sum(np.power(des, 2.0), axis=1)), (-1, 1))
        if not restart:
            if len(vel) > mig + 1:
                if vel[mig + 1].shape[0] == gru.size:
                    des = vel[mig + 1] + des
                    des = des / np.reshape(np.sqrt(np.sum(np.power(des, 2.0),
                                                          axis=1)), (-1, 1))
        while len(vel) <= mig + 1:
            vel.append(np.zeros((0, 3), dtype=float))
        vel[mig + 1] = des
        pos = np.where(np.reshape(mascara(), (-1, 1)), pos + des * 12.0, pos)

def particulasGravedad():
    global pos
    global gru
    global acGrav
    if gru.size > 0:
        grav = np.array([0, 0, -acGrav], dtype=float)
        pos = np.where(np.reshape(mascara(), (-1, 1)), pos + grav, pos)

def particulasDireccionadas(foc, atrae):
    global pos
    global gru
    if gru.size > 0:
        agiro = giraCentro() if flags[2] else 0
        if atrae:
            des = foc - pos
        else:
            des = pos - foc
        des = des / np.reshape(np.sqrt(np.sum(np.power(des, 2.0), axis=1)), (-1, 1))
        pos = np.where(np.reshape(mascara(), (-1, 1)), pos + des * 12.0, pos)
        giraTodo(agiro)

def particulasColision(g):
    global gru
    global pos
    global gvis
    if gru.size > 0:
        ggg = mascara()
        bias = np.zeros(gru.size, dtype=int) == 0
        bou = np.zeros((gru.size, 3), dtype=float)
        gvv = gvis[gru]
        for u in range(gru.size):
            bias[u] = False
            if ggg[u]:
                for v in range(gru.size):
                    if gvv[v] and bias[v]:
                        if ggg[v]:
                            d = np.power(pos[u, :] - pos[v, :], 2.0).sum()
                            if d <= 20:
                                bou[u] = bou[u] + (pos[u, :] - pos[v, :]) * 0.5
                                bou[v] = bou[v] + (pos[v, :] - pos[u, :]) * 0.5
                        elif gru[v] == g or g == -1:
                            d = np.power(pos[u, :] - pos[v, :], 2.0).sum()
                            if d <= 20:
                                bou[u] = bou[u] + (pos[u, :] - pos[v, :])
            elif gvv[u]:
                if gru[u] == g or g == -1:
                    for v in range(gru.size):
                        if ggg[v]:
                            if bias[v]:
                                d = np.power(pos[u, :] - pos[v, :], 2.0).sum()
                                if d <= 20:
                                    bou[v] = bou[v] + (pos[v, :] - pos[u, :])
        dis = np.sqrt(np.sum(np.power(bou, 2.0), axis=1))
        dis = np.where(dis == 0, 1, dis)
        bou = np.where(np.reshape(dis < 4.5, (-1, 1)), bou,
                       (bou / np.reshape(dis, (-1, 1))) * 4.5)
        pos = pos + bou
        return False in np.reshape(bou == 0, (1, -1))

def particulasLibres(g, limite, manual):
    global flags
    t = 0
    cronometro("", False)
    while True:
        if not particulasColision(g):
            break
        if manual:
            if flags[0]:
                dibujar()
            if input(tab() + str(t) + " repetir (S/n): ") == "n":
                break
        else:
            cronometro("ciclo " + str(t))
            t += 1
            if t >= abs(limite):
                break

def particulasDemoler(g, limite):
    particulasGravedad()
    particulasLibres(g, limite, False)
    limitar(True)

def particulasEnjambre(g, foc, atrae, limite, restart=False):
    particulasVelcidad(restart)
    particulasDireccionadas(foc, atrae)
    particulasLibres(g, limite, False)
    limitar(True)

def particulasTorcion(eje, azar):
    global pos
    global gru
    if gru.size > 0:
        agiro = giraCentro() if flags[2] else 0
        rot = np.cross(pos, eje)
        drot = np.sqrt(np.sum(np.power(rot, 2.0), axis=1))
        drot = np.where(drot == 0, 1, drot)
        rot = rot / np.reshape(drot, (-1, 1))
        if azar:
            des = np.random.random_sample((gru.size, 3)) * 2.0 - 1.0
            des = des / np.reshape(np.sqrt(np.sum(np.power(des, 2.0), axis=1)),
                                   (-1, 1))
            rot = rot + des
            rot = rot / np.reshape(np.sqrt(np.sum(np.power(rot, 2.0), axis=1)),
                                   (-1, 1))
        pos = np.where(np.reshape(mascara(), (-1, 1)), pos + rot * 12.0, pos)
        giraTodo(agiro)

def particulasTornado(g, limite):
    particulasTorcion(np.array([0, 0, 1]), True)
    particulasLibres(g, limite, False)
    limitar(True)

def crearAnomalias(porc):
    global gru
    global pos
    if gru.size > 0:
        ggg = mascara()
        des, base, mas = masaCentro(False)
        p = np.zeros((0, 3), dtype=float)
        bias = np.zeros(gru.size, dtype=int) == 0
        repit = int(np.floor(mas * porc))
        for r in range(repit):
            while True:
                u = np.random.randint(0, gru.size, 1)[0]
                if ggg[u] and bias[u]:
                    bias[u] = False
                    des = np.random.random_sample(3) * 2.0 - 1.0
                    des = des / magnitud(des)
                    p = np.append(p, [pos[u, :] + des * 6.0], axis=0)
                    break
        c = vecPintar(p.shape[0])
        g = vecGrupo(p.shape[0], grupoVacio())
        agregar(p, c, g)

# funciones de creacion:

def crearPoligono(pnts, cerrado):
    if len(pnts) > 1:
        if cerrado:
            for p in range(len(pnts)):
                if p == len(pnts) - 1:
                    crearRayo(pnts[p], pnts[0], False)
                else:
                    crearRayo(pnts[p], pnts[p + 1], False)
        else:
            for p in range(len(pnts)):
                if p == len(pnts) - 2:
                    crearRayo(pnts[p], pnts[p + 1])
                    break
                else:
                    crearRayo(pnts[p], pnts[p + 1], False)

def crearPunto(des):
    global mig
    if mig == -1:
        mig = grupoVacio()
    agregar(np.array([des]), [pintar()], mig)

def crearRelleno(des, g, ori, rec=0, fir=True):
    global mig
    global gru
    if fir:
        if mig == -1:
            mig = grupoVacio()
        agiro = giraCentro() if flags[2] else 0
    agregar(np.array([des]), [pintar()], mig)
    if rec < 980:
        otrop = [des + np.array([0, 6, 0]), des + np.array([6, 0, 0]),
                 des + np.array([0, -6, 0]), des + np.array([-6, 0, 0])]
        plim = np.array([ori[0] - 100, ori[1] - 100, -100000,
                         ori[0] + 100, ori[1] + 100, 100000])
        for pp in otrop:
            ok = False
            if not (False in (pp >= plim[:3]) or False in (pp <= plim[3:6])):
                ok = True
                for u in range(gru.size):
                    if gru[u] == g or g == -1 or gru[u] == mig:
                        if pos[u, 2] < pp[2] + 6 and pos[u, 2] > pp[2] - 6:
                            d = np.power(pos[u, :2] - pp[:2], 2.0).sum()
                            if d <= 25:
                                ok = False
                                break
            if ok:
                rec = crearRelleno(pp, g, ori, rec + 1, False)
    if fir:
        giraTodo(agiro)
    return rec

def crearMancha(des, g, ori, rec=0, fir=True):
    global mig
    global gru
    if fir:
        if mig == -1:
            mig = grupoVacio()
        agiro = giraCentro() if flags[2] else 0
    agregar(np.array([des]), [pintar()], mig)
    if rec < 980:
        otrop = [des + np.array([0, 6, 0]), des + np.array([6, 0, 0]),
                 des + np.array([0, -6, 0]), des + np.array([-6, 0, 0])]
        ind = np.arange(len(otrop))
        np.random.shuffle(ind)
        for i in range(len(otrop)):
            pp = otrop[ind[i]]
            ok = False
            d = np.power(ori[:2] - pp[:2], 2.0).sum()
            if d <= 2500:
                ok = True
                for u in range(gru.size):
                    if (gru[u] == g or g == -1) or gru[u] == mig:
                        if pos[u, 2] < pp[2] + 6 and pos[u, 2] > pp[2] - 6:
                            d = np.power(pos[u, :2] - pp[:2], 2.0).sum()
                            if d <= 25:
                                ok = False
                                break
            if ok:
                rec = crearMancha(pp, g, ori, rec + 1, False)
    if fir:
        giraTodo(agiro)
    return rec

def crearAro(des, rad, eje):
    global mig
    if mig == -1:
        mig = grupoVacio()
    if rad < 6:
        crearPunto(des)
    else:
        p = np.zeros((0, 3), dtype=float)
        rr = 2 * np.pi * rad
        pr = 360 * (rr / np.ceil(rr / 6)) / rr
        if eje == 0:
            for r in np.arange(0, 360, max(0.001, pr)):
                rr = np.deg2rad(r)
                n = np.array([des + np.array([0, rad * np.cos(rr), rad * np.sin(rr)])])
                p = np.append(p, n, axis=0)
        elif eje == 1:
            for r in np.arange(0, 360, max(0.001, pr)):
                rr = np.deg2rad(r)
                n = np.array([des + np.array([rad * np.cos(rr), 0, rad * np.sin(rr)])])
                p = np.append(p, n, axis=0)
        else:
            for r in np.arange(0, 360, max(0.001, pr)):
                rr = np.deg2rad(r)
                n = np.array([des + np.array([rad * np.cos(rr), rad * np.sin(rr), 0])])
                p = np.append(p, n, axis=0)
        c = vecPintar(p.shape[0])
        g = vecGrupo(p.shape[0], mig)
        agregar(p, c, g)

def crearCilindro(des, rad, alt, eje, solido=False):
    global mig
    if mig == -1:
        mig = grupoVacio()
    ph = alt / max(1, np.ceil(alt / 6))
    dd = des
    if eje == 0:
        for h in np.arange(0, alt + 1, max(0.001, ph)):
            if solido:
                crearCirculo(dd, rad, eje)
            else:
                crearAro(dd, rad, eje)
            dd = dd + np.array([ph, 0, 0])
    elif eje == 1:
        for h in np.arange(0, alt + 1, max(0.001, ph)):
            if solido:
                crearCirculo(dd, rad, eje)
            else:
                crearAro(dd, rad, eje)
            dd = dd + np.array([0, ph, 0])
    else:
        for h in np.arange(0, alt + 1, max(0.001, ph)):
            if solido:
                crearCirculo(dd, rad, eje)
            else:
                crearAro(dd, rad, eje)
            dd = dd + np.array([0, 0, ph])

def crearEsfera(des, rad, solido=False):
    global mig
    if mig == -1:
        mig = grupoVacio()
    if rad < 6:
        crearPunto(des)
    else:
        rr = np.pi * rad
        pr = 180 * (rr / np.ceil(rr / 6)) / rr
        for r in np.arange(0, 181, max(0.001, pr)):
            rr = np.deg2rad(r)
            dd = des + np.array([0, 0, rad * np.cos(rr)])
            if solido:
                crearCirculo(dd, rad * np.sin(rr), 2)
            else:
                crearAro(dd, rad * np.sin(rr), 2)

def crearCono(des, rad, alt, eje, solido=False):
    global mig
    if mig == -1:
        mig = grupoVacio()
    dis = magnitud([rad, alt])
    ang = np.arccos(rad / max(1, dis))
    ph = dis / max(1, np.ceil(dis / 6))
    dd = des
    if eje == 0:
        for h in np.arange(0, dis + 1, max(0.001, ph)):
            if solido:
                crearCirculo(dd, h * np.sin(ang) * (-rad / max(1, alt)) + rad, eje)
            else:
                crearAro(dd, h * np.sin(ang) * (-rad / max(1, alt)) + rad, eje)
            dd = dd + np.array([ph * np.sin(ang), 0, 0])
    elif eje == 1:
        for h in np.arange(0, dis + 1, max(0.001, ph)):
            if solido:
                crearCirculo(dd, h * np.sin(ang) * (-rad / max(1, alt)) + rad, eje)
            else:
                crearAro(dd, h * np.sin(ang) * (-rad / max(1, alt)) + rad, eje)
            dd = dd + np.array([0, ph * np.sin(ang), 0])
    else:
        for h in np.arange(0, dis + 1, max(0.001, ph)):
            if solido:
                crearCirculo(dd, h * np.sin(ang) * (-rad / max(1, alt)) + rad, eje)
            else:
                crearAro(dd, h * np.sin(ang) * (-rad / max(1, alt)) + rad, eje)
            dd = dd + np.array([0, 0, ph * np.sin(ang)])

def crearSilueta():
    global pos
    global gru
    global mat
    global shadow
    global flags
    if gru.size > 0:
        agiro = giraCentro() if flags[2] else 0
        p = np.zeros((0, 3), dtype=float)
        c = np.zeros((0, 4), dtype=int)
        pmax = np.max(pos[:, :2], axis=0) + 6
        pmin = np.min(pos[:, :2], axis=0) - 6
        ggg = mascara()
        ziz = int(mat[0] / 2)
        for x in range(-ziz, ziz, 6):
            for y in range(-ziz, ziz, 6):
                xy = np.array([x, y], dtype=float)
                if not (False in (xy >= pmin) or False in (xy <= pmax)):
                    for u in range(gru.size):
                        if ggg[u] and pos[u, 2] >= 0:
                            d = np.power(pos[u, :2] - xy, 2.0).sum()
                            if d <= 36:
                                p = np.append(p, [np.array([x, y, 0],
                                                           dtype=float)], axis=0)
                                c = np.append(c, [shadow], axis=0)
                                break
        g = vecGrupo(p.shape[0], grupoVacio())
        agregar(p, c, g)
        giraTodo(agiro)

def crearSombra():
    global gru
    global mat
    global shadow
    global flags
    global luz
    global cnfgluz
    if gru.size > 0:
        agiro = giraCentro() if flags[2] else 0
        p = np.zeros((0, 3), dtype=float)
        c = np.zeros((0, 4), dtype=int)
        agru, zona, plim = zonificarGeneral()
        bias = mascara()
        if flags[3]:
            lux = luz
            extra = 0
        else:
            lux = (luz / magnitud(luz)) * cnfgluz[2]
            extra = cnfgluz[2] - magnitud(np.array([mat[0], mat[0], mat[1]]))
        ziz = int(mat[0] / 2)
        for x in range(-ziz, ziz, 6):
            for y in range(-ziz, ziz, 6):
                xy = np.array([x, y, 0], dtype=float)
                impac = rayoColision(lux, xy, agru, zona, extra, bias, plim)
                if impac != -1:
                    p = np.append(p, [xy], axis=0)
                    c = np.append(c, [shadow], axis=0)
        g = vecGrupo(p.shape[0], grupoVacio())
        agregar(p, c, g)
        giraTodo(agiro)

def crearMarco(des, talla, eje):
    global mig
    if mig == -1:
        mig = grupoVacio()
    if magnitud(talla) < 6:
        crearPunto(des)
    elif talla[0] < 6 and talla[1] >= 6:
        if eje == 0:
            crearCilindro(des, 0, talla[1], 1)
        if eje == 1:
            crearCilindro(des, 0, talla[1], 2)
        else:
            crearCilindro(des, 0, talla[1], 1)
    elif talla[0] >= 6 and talla[1] < 6:
        if eje == 0:
            crearCilindro(des, 0, talla[1], 2)
        if eje == 1:
            crearCilindro(des, 0, talla[1], 0)
        else:
            crearCilindro(des, 0, talla[1], 0)
    else:
        p = np.zeros((0, 3), dtype=float)
        px = talla[0] / max(1, np.ceil(talla[0] / 6))
        py = talla[1] / max(1, np.ceil(talla[1] / 6))
        if eje == 0:
            for x in np.arange(0, talla[0] + 1, max(0.001, px)):
                n = [des + np.array([0, py, x])]
                p = np.append(p, n, axis=0)
                n = [des + np.array([0, talla[1] - py, x])]
                p = np.append(p, n, axis=0)
            for y in np.arange(py, talla[1] + 1 - py, max(0.001, py)):
                n = [des + np.array([0, y, 0])]
                p = np.append(p, n, axis=0)
                n = [des + np.array([0, y, talla[0]])]
                p = np.append(p, n, axis=0)
        elif eje == 1:
            for x in np.arange(0, talla[0] + 1, max(0.001, px)):
                n = [des + np.array([x, 0, py])]
                p = np.append(p, n, axis=0)
                n = [des + np.array([x, 0, talla[1] - py])]
                p = np.append(p, n, axis=0)
            for y in np.arange(py, talla[1] + 1 - py, max(0.001, py)):
                n = [des + np.array([0, 0, y])]
                p = np.append(p, n, axis=0)
                n = [des + np.array([talla[0], 0, y])]
                p = np.append(p, n, axis=0)
        else:
            for x in np.arange(0, talla[0] + 1, max(0.001, px)):
                n = [des + np.array([x, py, 0])]
                p = np.append(p, n, axis=0)
                n = [des + np.array([x, talla[1] - py, 0])]
                p = np.append(p, n, axis=0)
            for y in np.arange(py, talla[1] + 1 - py, max(0.001, py)):
                n = [des + np.array([0, y, 0])]
                p = np.append(p, n, axis=0)
                n = [des + np.array([talla[0], y, 0])]
                p = np.append(p, n, axis=0)
        c = vecPintar(p.shape[0])
        g = vecGrupo(p.shape[0], mig)
        agregar(p, c, g)

def crearCuadro(des, talla, eje):
    global mig
    if mig == -1:
        mig = grupoVacio()
    if magnitud(talla) < 6:
        crearPunto(des)
    elif talla[0] < 6 and talla[1] >= 6:
        if eje == 0:
            crearCilindro(des, 0, talla[1], 1)
        if eje == 1:
            crearCilindro(des, 0, talla[1], 2)
        else:
            crearCilindro(des, 0, talla[1], 1)
    elif talla[0] >= 6 and talla[1] < 6:
        if eje == 0:
            crearCilindro(des, 0, talla[1], 2)
        if eje == 1:
            crearCilindro(des, 0, talla[1], 0)
        else:
            crearCilindro(des, 0, talla[1], 0)
    else:
        p = np.zeros((0, 3), dtype=float)
        px = talla[0] / max(1, np.ceil(talla[0] / 6))
        py = talla[1] / max(1, np.ceil(talla[1] / 6))
        if eje == 0:
            for x in np.arange(0, talla[0] + 1, max(0.001, px)):
                for y in np.arange(py, talla[1] + 1 - py, max(0.001, py)):
                    n = [des + np.array([0, y, x])]
                    p = np.append(p, n, axis=0)
        elif eje == 1:
            for x in np.arange(0, talla[0] + 1, max(0.001, px)):
                for y in np.arange(py, talla[1] + 1 - py, max(0.001, py)):
                    n = [des + np.array([x, 0, y])]
                    p = np.append(p, n, axis=0)
        else:
            for x in np.arange(0, talla[0] + 1, max(0.001, px)):
                for y in np.arange(py, talla[1] + 1 - py, max(0.001, py)):
                    n = [des + np.array([x, y, 0])]
                    p = np.append(p, n, axis=0)
        c = vecPintar(p.shape[0])
        g = vecGrupo(p.shape[0], mig)
        agregar(p, c, g)

def crearCaja(des, talla, eje, solido=False):
    global mig
    if mig == -1:
        mig = grupoVacio()
    ph = talla[2] / max(1, np.ceil(talla[2] / 6))
    dd = des
    if eje == 0:
        for h in np.arange(0, talla[2] + 1, max(0.001, ph)):
            if solido:
                crearCuadro(dd, talla[:2], eje)
            else:
                crearMarco(dd, talla[:2], eje)
            dd = dd + np.array([ph, 0, 0])
    elif eje == 1:
        for h in np.arange(0, talla[2] + 1, max(0.001, ph)):
            if solido:
                crearCuadro(dd, talla[:2], eje)
            else:
                crearMarco(dd, talla[:2], eje)
            dd = dd + np.array([0, ph, 0])
    else:
        for h in np.arange(0, talla[2] + 1, max(0.001, ph)):
            if solido:
                crearCuadro(dd, talla[:2], eje)
            else:
                crearMarco(dd, talla[:2], eje)
            dd = dd + np.array([0, 0, ph])

def crearPiramide(des, talla, eje, solido=False):
    global mig
    if mig == -1:
        mig = grupoVacio()
    ph = talla[2] / max(1, np.ceil(talla[2] / 6))
    dd = des
    atll = talla[:2]
    for h in np.arange(0, talla[2] + 1 - ph, max(0.001, ph)):
        tll = h * (-talla[:2] / max(1, talla[2])) + talla[:2]
        if solido:
            crearCuadro(dd, tll, eje)
        else:
            crearMarco(dd, tll, eje)
        cmb = (atll - tll) / 2
        atll = tll
        if eje == 0:
            dd = dd + np.array([ph, cmb[1], cmb[0]])
        elif eje == 1:
            dd = dd + np.array([cmb[0], ph, cmb[1]])
        else:
            dd = dd + np.array([cmb[0], cmb[1], ph])

def crearCirculo(des, rad, eje):
    global mig
    if mig == -1:
        mig = grupoVacio()
    if rad < 6:
        crearPunto(des)
    else:
        pr = rad / max(1, np.ceil(rad / 6))
        for r in np.arange(0, rad + 1, max(0.001, pr)):
            crearAro(des, r, eje)

def crearRayo(ini, fin, ultimo=True):
    global mig
    if mig == -1:
        mig = grupoVacio()
    pp = ini
    vel = fin - ini
    dis = magnitud(vel)
    if dis < 6:
        crearPunto(ini)
    else:
        pv = dis / max(1, np.ceil(dis / 6))
        vel = (vel / dis) * pv
        pnts = []
        for v in np.arange(0, dis + 1, max(0.001, pv)):
            pnts.append(pp)
            pp = pp + vel
        for p in range(len(pnts) - (0 if ultimo else 1)):
            crearPunto(pnts[p])

def crearAzarCilindro(des, rad, alt, eje, porc):
    global mig
    if mig == -1:
        mig = grupoVacio()
    p = np.zeros((0, 3), dtype=float)
    dmin = np.power(rad, 2.0)
    vol = (np.pi * dmin * alt) / volVox()
    for r in range(int(vol * porc)):
        while True:
            if eje == 0:
                new = np.random.rand(3) * np.array([alt, 2 * rad, 2 * rad]) -\
                      np.array([0, rad, rad])
                d = np.power(new[1:3], 2.0).sum()
                if d <= dmin:
                    p = np.append(p, [new + des], axis=0)
                    break
            elif eje == 1:
                new = np.random.rand(3) * np.array([2 * rad, alt, 2 * rad]) -\
                      np.array([rad, 0, rad])
                d = np.power(new[0:3:2], 2.0).sum()
                if d <= dmin:
                    p = np.append(p, [new + des], axis=0)
                    break
            else:
                new = np.random.rand(3) * np.array([2 * rad, 2 * rad, alt]) -\
                      np.array([rad, rad, 0])
                d = np.power(new[:2], 2.0).sum()
                if d <= dmin:
                    p = np.append(p, [new + des], axis=0)
                    break
    c = vecPintar(p.shape[0])
    g = vecGrupo(p.shape[0], mig)
    agregar(p, c, g)

def crearAzarEsfera(des, rad, porc):
    global mig
    if mig == -1:
        mig = grupoVacio()
    p = np.zeros((0, 3), dtype=float)
    dmin = np.power(rad, 2.0)
    vol = ((4 / 3) * np.pi * np.power(rad, 3.0)) / volVox()
    for r in range(int(vol * porc)):
        while True:
            new = (np.random.rand(3) * 2 - 1) * rad
            d = np.power(new, 2.0).sum()
            if d <= dmin:
                p = np.append(p, [new + des], axis=0)
                break
    c = vecPintar(p.shape[0])
    g = vecGrupo(p.shape[0], mig)
    agregar(p, c, g)

def crearArbol(des, alt, rad1, rad2, tipo):
    global mig
    amig = mig
    gtronco = grupoVacio()
    mig = gtronco
    altu = alt * 0.75 + alt * 0.25 * np.random.ranf()
    radi = rad1 * 0.5 + rad1 * 0.5 * np.random.ranf()
    crearCilindro(des, radi, altu, 2)
    pintarClasico("cafe")
    ghojas = grupoVacio()
    mig = ghojas
    if tipo == 0:
        dd = des + np.array([0, 0, altu])
        radi = (rad2 * 0.8 + rad2 * 0.2 * np.random.ranf())
        crearEsfera(dd, radi)
    elif tipo == 1:
        dd = des + np.array([0, 0, altu])
        radi = (rad2 * 0.8 + rad2 * 0.2 * np.random.ranf())
        crearAzarEsfera(dd, radi, 0.5 + 0.25 * np.random.ranf())
    elif tipo == 2:
        dd = des + np.array([0, 0, altu * 0.75])
        radi = (rad2 * 0.8 + rad2 * 0.2 * np.random.ranf())
        crearCilindro(dd, radi, altu * 0.5, 2)
        crearCirculo(dd + np.array([0, 0, altu * 0.5]), radi - 6, 2)
    elif tipo == 3:
        dd = des + np.array([0, 0, altu * 0.75])
        radi = (rad2 * 0.8 + rad2 * 0.2 * np.random.ranf())
        crearAzarCilindro(dd, radi, altu * 0.5, 2, 0.5 + 0.25 * np.random.ranf())
    elif tipo == 4:
        dd = des + np.array([0, 0, altu * 0.5])
        radi = (rad2 * 0.8 + rad2 * 0.2 * np.random.ranf())
        crearCono(dd, radi, altu * 1.5, 2)
    elif tipo == 5:
        dd = des + np.array([0, 0, altu * 0.5])
        radi = (rad2 * 0.8 + rad2 * 0.2 * np.random.ranf())
        crearCono(dd, radi, altu * 0.5, 2)
        dd = dd + np.array([0, 0, altu * 0.4])
        crearCono(dd, radi * 0.75, altu * 0.5, 2)
        dd = dd + np.array([0, 0, altu * 0.3])
        crearCono(dd, radi * 0.5, altu * 0.55, 2)
    pintarClasico("verde")
    mig = gtronco
    mezclarGrupos(ghojas)
    if amig != -1:
        mig = amig
        mezclarGrupos(gtronco)

def crearRueda(des, rad, anch):
    global mig
    amig = mig
    grueda = grupoVacio()
    mig = grueda
    crearCilindro(des + np.array([-anch / 2, 0, 0]), rad, anch, 0)
    crearCirculo(des + np.array([-anch / 2, 0, 0]), rad - 6, 0)
    crearCirculo(des + np.array([anch / 2, 0, 0]), rad - 6, 0)
    pintarClasico("negro")
    eliminarCilindro(des + np.array([-anch, 0, 0]), rad * 0.666, anch * 2, 0)
    grin = grupoVacio()
    mig = grin
    crearCirculo(des + np.array([-(anch / 2 - 6), 0, 0]), rad * 0.666, 0)
    crearCirculo(des + np.array([anch / 2 - 6, 0, 0]), rad * 0.666, 0)
    pintarClasico("gris")
    mig = grueda
    mezclarGrupos(grin)
    if amig != -1:
        mig = amig
        mezclarGrupos(grueda)

def crearParedes(pnts, des, alt, cerrado):
    global mig
    amig = mig
    gpared = grupoVacio()
    mig = gpared
    for p in range(len(pnts)):
        pnts[p] = pnts[p] * np.array([1, 1, 0])
    crearPoligono(pnts, cerrado)
    traslacion(np.array([0, 0, des]))
    estrucion(alt, 2)
    if amig != -1:
        mig = amig
        mezclarGrupos(gpared)

def crearRevolucion(pnts, cerrado):
    global mig
    amig = mig
    gpared = grupoVacio()
    mig = gpared
    for p in range(len(pnts)):
        pnts[p] = np.array([pnts[p][0], 0, pnts[p][1]])
    crearPoligono(pnts, cerrado)
    revolucion()
    if amig != -1:
        mig = amig
        mezclarGrupos(gpared)

def obraPNG(img):
    global mat
    global cen
    # escalar la imagen
    img = pg.transform.smoothscale(img, mat)
    # proceder a crear voxels
    agiro = giraCentro() if flags[2] else 0
    p = np.zeros((0, 3), dtype=float)
    c = np.zeros((0, 4), dtype=int)
    for x in range(6, mat[0], 6):
        for y in range(6, mat[1], 6):
            ccc = np.zeros(4, dtype=int)
            for xx in range(-2, 3, 2):
                for yy in range(-2, 3, 2):
                    ccc = ccc + img.get_at((x + xx, y + yy))
            ccc = np.clip(np.array(ccc / 9, dtype=int), 0, 255)
            if ccc[3] > 25:
                p = np.append(p, [np.array([x - cen[0],
                                            y - cen[1], 0])], axis=0)
                c = np.append(c, [ccc], axis=0)
    g = vecGrupo(p.shape[0], grupoVacio())
    agregar(p, c, g)
    giraTodo(agiro)

def crearTecho(des, talla):
    global mig
    if mig == -1:
        mig = grupoVacio()
    anch = talla[0] / 2.0
    hip = magnitud(np.array([anch, 0, talla[2]]))
    ph = hip / max(1, np.ceil(hip / 6))
    di = (np.array([anch, 0, talla[2]]) / hip) * ph
    d1 = des + np.array([0, -talla[1], 0])
    n = 0
    for h in np.arange(0, hip + 1, max(0.001, ph)):
        crearCilindro(d1, 0, talla[1], 1)
        d1 = d1 + di
        n += 1
    d2 = des + np.array([anch * 2, -talla[1], 0])
    for h in np.arange(0, hip + 1, max(0.001, ph)):
        if n <= 1:
            break
        else:
            crearCilindro(d2, 0, talla[1], 1)
            d2 = d2 + di * np.array([-1, 1, 1])
        n -= 1

def crearRampa(des, talla, ang):
    global mig
    amig = mig
    gram = grupoVacio()
    mig = gram
    hip = magnitud(np.array([talla[0], 0, talla[2]]))
    ph = hip / max(1, np.ceil(hip / 6))
    di = (np.array([talla[0], 0, talla[2]]) / hip) * ph
    dd = des
    for h in np.arange(0, hip + 1, max(0.001, ph)):
        crearCilindro(dd, 0, talla[1], 1)
        dd = dd + di
    rotacion(des, np.array([0, 0, ang]))
    if amig != -1:
        mig = amig
        mezclarGrupos(gram)

def crearPelo(ini, direc, larg, cambio, gravedad, foco=[]):
    global mig
    if mig == -1:
        mig = grupoVacio()
    if larg < 6:
        crearPunto(ini)
    else:
        pp = ini
        dd = direc / magnitud(direc)
        pv = larg / max(1, np.ceil(larg / 6))
        for v in np.arange(0, larg + 1, max(0.001, pv)):
            crearPunto(pp)
            pp = pp + dd * pv
            des = np.random.random_sample(3) * 2.0 - 1.0
            if gravedad:
                des[2] = des[2] - np.random.ranf()
            des = (des / magnitud(des)) * cambio
            dd = dd + des
            if len(foco) == 1:
                des = foco[0][:3] - pp
                des = (des / magnitud(des)) * np.random.ranf() * foco[0][3]
            dd = dd + des
            dd = dd / magnitud(dd)

def crearDemo():
    global mig
    amig = mig
    # muralla exterior
    g0 = grupoVacio()
    mig = g0
    crearCilindro(np.zeros(3), 75, 60, 2)
    crearCilindro(np.zeros(3), 81, 60, 2)
    pintarClasico("caqui")
    eliminarCilindro(np.array([0, -75, 0]), 30, 150, 2)
    eliminarCaja(np.array([-15, 60, 0]), np.array([30, 100, 50]))
    # torre de roca
    g1 = grupoVacio()
    mig = g1
    crearCilindro(np.array([0, -75, 0]), 30, 150, 2)
    pintarClasico("gris")
    aux = grupoVacio()
    mig = aux
    crearCilindro(np.array([0, -75, 0]), 24, 150, 2)
    pintarClasico("morado")
    mig = g1
    mezclarGrupos(aux)
    eliminarCaja(np.array([-10, -60, 0]), np.array([20, 60, 50]))
    eliminarCilindro(np.array([0, -300, 90]), 15, 600, 1)
    des, base, mas = masaCentro(False)
    rotacion(des, np.array([0, 0, 90]))
    eliminarCilindro(np.array([0, -300, 90]), 15, 600, 1)
    rotacion(des, np.array([0, 0, -90]))
    # punta de la torre
    g2 = grupoVacio()
    mig = g2
    crearCono(np.array([0, -75, 140]), 50, 90, 2)
    pintarClasico("rojo")
    # el pelo
    g6 = grupoVacio()
    mig = g6
    crearPelo(np.array([0, -75, 230]), np.ones(3), 100, 0.6, True)
    pintarClasico("agua")
    # girar completo
    mig = -1
    rotacion(np.zeros(3), np.array([0, 0, -45]))
    # abre espacio en muralla
    mig = g0
    eliminarCilindro(np.array([75, -20, 0]), 28, 105, 2)
    eliminarEsfera(np.array([-50, 50, 75]), 45)
    # casucha de ladrillo
    g3 = grupoVacio()
    mig = g3
    crearCaja(np.array([30, -45, 0]), np.array([80, 60, 105]), 2)
    crearCaja(np.array([36, -39, 0]), np.array([68, 48, 105]), 2)
    pintarClasico("naranja")
    rotacion(np.zeros(3), np.array([0, 0, -90]))
    eliminarCaja(np.array([-25, -40, 0]), np.array([25, 100, 50]))
    eliminarCaja(np.array([-25, -200, 40]), np.array([25, 160, 20]))
    eliminarCilindro(np.array([-100, -75, 80]), 15, 200, 0)
    des, base, mas = masaCentro(False)
    rotacion(des, np.array([0, 0, -22]))
    rotacion(np.zeros(3), np.array([0, 0, 90]))
    # techo de paja
    g4 = grupoVacio()
    mig = g4
    crearTecho(np.array([10, 35, 90]), np.array([120, 100, 60]))
    pintarClasico("amarillo")
    des, base, mas = masaCentro(False)
    rotacion(des, np.array([0, 0, -22]))
    # arbolito
    g5 = grupoVacio()
    mig = g5
    crearArbol(np.array([-30, 30, 0]), 70, 12, 30, 0)
    # juntar las cosas
    mig = g0
    mezclarGrupos(g1)
    mezclarGrupos(g2)
    mezclarGrupos(g3)
    mezclarGrupos(g4)
    mezclarGrupos(g5)
    mezclarGrupos(g6)
    if amig != -1:
        mig = amig
        mezclarGrupos(g0)

def crearMonigote(base, cuell, fren, extrem, fem, alt):
    global mig
    amig = mig
    esc = alt / 10
    # vectores unitarios relativos
    ucolu = (cuell - base) / magnitud(cuell - base)
    ulado = vecUniCruz(ucolu, fren)
    ufren = vecUniCruz(ulado, ucolu)
    # crear puntos clave (inf i, inf d, sup i, sup d)
    union = [base + ucolu * esc * 0.25 + ulado * esc * 0.75,
             base + ucolu * esc * 0.25 + ulado * esc * -0.75,
             base + ucolu * esc * 3.75 + ulado * esc * 1.25,
             base + ucolu * esc * 3.75 + ulado * esc * -1.25]
    inflex = [base + ucolu * esc + ufren * esc * 3 + ulado * esc * 2,
              base + ucolu * esc + ufren * esc * 3 + ulado * esc * -2,
              base + ucolu * esc * 2 + ufren * esc * -2 + ulado * esc * 1.5,
              base + ucolu * esc * 2 + ufren * esc * -2 + ulado * esc * -1.5]
    long = [esc * 4.25, esc * 4.25, esc * 3.75, esc * 3.75]
    # limitar longitud extremidades
    for i in range(4):
        aux = magnitud(extrem[i] - union[i])
        if aux > long[i]:
            extrem[i] = union[i] + ((extrem[i] - union[i]) / aux) * long[i]
    # para cada extremidad calcular el punto de quiebre
    quieb = []
    for i in range(4):
        candi = []
        while True:
            aux = np.random.random_sample(3) * 2.0 - 1.0
            aux = (aux / magnitud(aux)) * long[i] / 2
            dd = magnitud(extrem[i] - (union[i] + aux))
            if dd > (long[i] / 2) * 0.9 and dd < (long[i] / 2) * 1.1:
                candi.append(aux)
                if len(candi) >= 16:
                    break
        aux = 0
        mej = 100000
        for c in range(len(candi)):
            dd = magnitud(inflex[i] - (union[i] + candi[c]))
            if dd < mej:
                mej = dd
                aux = c
        quieb.append(union[i] + candi[aux])
    # crear las cosas graficamente
    g0 = grupoVacio()
    mig = g0
    crearEsfera(base + ucolu * esc * 5, esc)
    pintarClasico("rosa")
    g1 = grupoVacio()
    mig = g1
    if fem == 0:
        crearEsfera(base + ucolu * esc, esc)
        crearEsfera(base + ucolu * esc * 3, esc)
    elif fem == 1:
        crearRayo(base, base + ucolu * esc * 4)
        crearRayo(union[0], union[1])
        crearRayo(union[2], union[3])
    elif fem == 2:
        crearCilindro(base, esc * 0.5, esc * 2, 2)
        crearCilindro(base + ucolu * esc * 2, esc * 1, esc * 2, 2)
        #rotacion(base, )
    pintarGrupo()
    g2 = grupoVacio()
    mig = g2
    for i in range(4):
        crearRayo(union[i], quieb[i], False)
        crearRayo(quieb[i], extrem[i])
    pintarClasico("rosa")
    g3 = grupoVacio()
    mig = g3
    crearPunto(base + ucolu * esc * 5 + ulado * esc * 0.5 + ufren * esc)
    crearPunto(base + ucolu * esc * 5 + ulado * esc * -0.5 + ufren * esc)
    pintarClasico("negro")
    # mezclar grupos
    mig = g0
    mezclarGrupos(g1)
    mezclarGrupos(g2)
    mezclarGrupos(g3)
    if amig != -1:
        mig = amig
        mezclarGrupos(g0)

def crearManiqui(des, alt, brazos, ang):
    global mig
    amig = mig
    esc = alt / 10
    # partes de piel
    g0 = grupoVacio()
    mig = g0
    crearEsfera(des + np.array([0, 0, esc * 9]), esc)
    crearRayo(des + np.array([esc, 0, 0]), des +
              np.array([esc * 0.5, 0, esc * 4]))
    crearRayo(des + np.array([-esc, 0, 0]), des +
              np.array([-esc * 0.5, 0, esc * 4]))
    hom = [des + np.array([esc, 0, esc * 7.5]),
           des + np.array([-esc, 0, esc * 7.5])]
    if brazos == 1:
        crearRayo(hom[0], hom[0] + np.array([esc * 0.5, esc * 4, 0]))
        crearRayo(hom[1], hom[1] + np.array([-esc * 0.5, esc * 4, 0]))
    elif brazos == 2:
        crearRayo(hom[0], hom[0] + np.array([esc * 4, 0, 0]))
        crearRayo(hom[1], hom[1] + np.array([-esc * 4, 0, 0]))
    elif brazos == 3:
        crearRayo(hom[0], hom[0] + np.array([esc * 0.5, 0, -esc * 4]))
        crearRayo(hom[1], hom[1] + np.array([-esc * 0.5, 0, -esc * 4]))
    elif brazos == 4:
        crearRayo(hom[0], hom[0] + np.array([esc * 3, 0, esc * 3]))
        crearRayo(hom[1], hom[1] + np.array([-esc * 3, 0, esc * 3]))
    rotacion(des, np.array([0, 0, ang - 90]))
    pintarClasico("rosa")
    # cuerpo
    g1 = grupoVacio()
    mig = g1
    crearCilindro(des + np.array([0, 0, esc * 4.5]), esc * 0.8, esc * 3, 2)
    pintarGrupo()
    # mezclar grupos
    mig = g0
    mezclarGrupos(g1)
    if amig != -1:
        mig = amig
        mezclarGrupos(g0)

# funciones de dibujado:

def pintarClasico(nombre):
    global ecol
    global acol
    aacol = acol.copy()
    aecol = ecol.copy()
    galeriaTexturas()
    elegirTextura(nombre, False)
    pintarGrupo()
    ecol = aecol
    acol = aacol

def colorAzar(payaso):
    global acol
    c1 = np.random.randint(0, 256, 3, dtype=int)
    c1 = np.append(c1, 255)
    if payaso:
        c2 = np.random.randint(0, 256, 3, dtype=int)
        c2 = np.append(c2, 255)
        c3 = np.random.randint(0, 256, 3, dtype=int)
        c3 = np.append(c3, 255)
    else:
        c2 = c1.copy()
        c2[:3] = np.clip(c2[:3] + np.random.randint(-50, 50, 3,
                                                    dtype=int), 0, 255)
        c3 = c1.copy()
        c3[:3] = np.clip(c3[:3] + np.random.randint(-50, 50, 3,
                                                    dtype=int), 0, 255)
    acol = [c1, c2, c3]

def nuevoColor(c1, c2, c3):
    global acol
    if np.array_equal(c2, np.array([255, 255, 255, 255], dtype=int)):
        c2 = c1.copy()
    if np.array_equal(c3, np.array([255, 255, 255, 255], dtype=int)):
        c3 = c2.copy()
    acol = [c1, c2, c3]

def nuevaTextura(nombre, c1, c2, c3):
    global acol
    global ecol
    if len(nombre) > 0:
        nuevoColor(c1, c2, c3)
        ind = -1
        for t in range(len(ecol)):
            if ecol[t][0] == nombre:
                ind = t
                break
        if ind == -1:
            ecol.append([nombre, acol.copy()])
        else:
            ecol[ind] = [nombre, acol.copy()]

def unicaTextura():
    global ecol
    n = 1
    while len(ecol) > n:
        elim = False
        for e in range(len(ecol)):
            if e != n and ecol[e][0] == ecol[n][0]:
                ecol.pop(n)
                elim = True
                break
        if not elim:
            n += 1

def verTexturas():
    global ecol
    print("***Texturas***")
    for t in ecol:
        print(tab() + t[0])

def eliminarTextura(nombre):
    global ecol
    if nombre == "-1":
        ecol = []
        print(tab() + "Ok")
    else:
        for t in range(len(ecol) - 1, -1, -1):
            if ecol[t][0] == nombre:
                ecol.pop(t)
                print(tab() + "Ok")

def elegirTextura(nombre, show=True):
    global ecol
    global acol
    for t in ecol:
        if t[0] == nombre:
            acol = t[1].copy()
            if show:
                print(tab() + "Ok")
            break

def pintarGrupo():
    global col
    global gru
    ggg = mascara()
    for u in range(gru.size):
        if ggg[u]:
            col[u, :] = pintar()

def pintarTransparencia(alp, setear):
    global col
    global gru
    ggg = mascara()
    if setear:
        for u in range(gru.size):
            if ggg[u]:
                col[u, 3] = int(np.clip(alp, 0, 255))
    else:
        for u in range(gru.size):
            if ggg[u]:
                col[u, 3] = int(np.clip(col[u, 3] * alp, 0, 255))

def dibuContorno(s, c):
    global contorno
    if contorno == 1:
        pg.draw.circle(s, (0, 0, 0, 255), (6, 6), 6, 1)
    elif contorno == 2:
        pg.draw.circle(s, (0, 0, 0, 128), (6, 6), 6, 1)
    elif contorno == 3:
        pg.draw.circle(s, c, (6, 6), 6, 1)
    elif contorno == 4:
        cc = np.clip(c - np.array([50, 50, 50, 0], dtype=int), 0, 255)
        pg.draw.circle(s, cc, (6, 6), 6, 1)
    elif contorno == 5:
        cc = c * np.array([0.8, 0.8, 0.8, 1], dtype=float)
        cc = np.array(np.clip(cc, 0, 255), dtype=int)
        pg.draw.circle(s, cc, (6, 6), 6, 1)
    elif contorno == 6:
        cc = c * np.array([0.5, 0.5, 0.5, 1], dtype=float)
        cc = np.array(np.clip(cc, 0, 255), dtype=int)
        pg.draw.circle(s, cc, (6, 6), 6, 1)

def dibujar(grupal=False, maraton=False):
    global flags
    global gru
    global mat
    global flags
    global fondos
    global cuadricula
    if gru.size > 0:
        if grupal:
            ss = dibujaGrupo()
        else:
            if flags[1]:
                if maraton:
                    cronometro("", False)
                ss = dibujaLuz(maraton)
                if maraton:
                    cronometro("", True, True)
            else:
                ss = dibujaBasico()
    elif grupal:
        ss = dibujaGrupo()
    else:
        ss = pg.Surface(mat, pg.SRCALPHA, 32)
        ss.fill((0, 0, 0, 0))
    # dibuja las cosas en pantalla
    surf = pg.display.get_surface()
    tll = surf.get_size()
    tll = (int((tll[0] - 40) / 2), int(tll[1] - 20))
    sss = pg.Surface(tll, pg.SRCALPHA, 32)
    sss.fill((200, 200, 200, 255))
    surf.blit(sss, (10, 10))
    if flags[6] and fondos[0][0]:
        surf.blit(fondos[1][0], (10, 10))
    sss = ss.copy()
    sss = pg.transform.scale(sss, tll)
    surf.blit(sss, (10, 10))
    if not maraton and flags[5]:
        esc = tll[1] / mat[1]
        # plano eje y
        s, v = dibujaPlanos(1)
        s = pg.transform.scale(s, (int(tll[0] / 2),
                                   int((s.get_size()[1] * esc) / 2)))
        sss = pg.Surface(s.get_size(), pg.SRCALPHA, 32)
        sss.fill((200, 200, 200, 255))
        surf.blit(sss, (tll[0] + 20, 10))
        if flags[6] and fondos[0][1]:
            surf.blit(fondos[1][1], (tll[0] + 20, 10))
        sss.fill((0, 0, 0, 0))
        sss.blit(cuadricula, (0, 0))
        surf.blit(sss, (tll[0] + 20, 10))
        surf.blit(s, (tll[0] + 20, 10))
        # plano eje x
        s, v = dibujaPlanos(0, v)
        s = pg.transform.scale(s, (int(tll[0] / 2),
                                   int((s.get_size()[1] * esc) / 2)))
        sss = pg.Surface(s.get_size(), pg.SRCALPHA, 32)
        sss.fill((200, 200, 200, 255))
        surf.blit(sss, (tll[0] * 1.5 + 30, 10))
        if flags[6] and fondos[0][2]:
            surf.blit(fondos[1][2], (tll[0] * 1.5 + 30, 10))
        sss.fill((0, 0, 0, 0))
        sss.blit(cuadricula, (0, 0))
        surf.blit(sss, (tll[0] * 1.5 + 30, 10))
        surf.blit(s, (tll[0] * 1.5 + 30, 10))
        des = sss.get_size()[1]
        # plano eje z
        s, v = dibujaPlanos(2, v)
        s = pg.transform.scale(s, (int(tll[0] / 2), int(tll[0] / 2)))
        sss = pg.Surface(s.get_size(), pg.SRCALPHA, 32)
        sss.fill((200, 200, 200, 255))
        surf.blit(sss, (tll[0] + 20, des + 20))
        if flags[6] and fondos[0][3]:
            surf.blit(fondos[1][3], (tll[0] + 20, des + 20))
        sss.fill((0, 0, 0, 0))
        sss.blit(cuadricula, (0, sss.get_size()[1] -
                              cuadricula.get_size()[1]))
        surf.blit(sss, (tll[0] + 20, des + 20))
        surf.blit(s, (tll[0] + 20, des + 20))
    pg.display.flip()
    return ss

def dibujaBasico():
    global pos
    global col
    global gru
    global gvis
    global cam
    global cen
    global mat
    global flags
    ss = pg.Surface(mat, pg.SRCALPHA, 32)
    ss.fill((0, 0, 0, 0))
    s = pg.Surface((12, 12), pg.SRCALPHA, 32)
    vie = np.array((-1, -1, -1, -1), dtype=int)
    # dibujar los voxels
    dep = np.argsort(np.sum(np.power(pos - cam, 2.0), axis=1))
    apos = pos.copy()
    if flags[4]:
        apos[:, 1] = np.subtract(apos[:, 1], apos[:, 2] * 0.5)
    else:
        apos[:, 1] = np.subtract(apos[:, 1], apos[:, 2])
    apos = apos[:, :2] + (cen - 6)
    gvv = gvis[gru]
    for d in range(len(dep) - 1, -1, -1):
        dd = dep[d]
        if gvv[dd]:
            if not np.array_equal(vie, col[dd, :]):
                s.fill((0, 0, 0, 0))
                pg.draw.circle(s, col[dd, :], (6, 6), 5)
                dibuContorno(s, col[dd, :])
                vie = col[dd, :]
            ss.blit(s, (apos[dd, 0], apos[dd, 1]))
    return ss

def dibujaLuz(maraton=False):
    global cam
    global cen
    global mat
    global luz
    global flags
    global cnfgluz
    if not maraton:
        cronometro("", False)
    apos, aacol, agru, zona, plim = zonificar()
    if not maraton:
        cronometro("zonificar")
    # calcular iluminacion
    milu = np.zeros(agru.size, dtype=float)
    bias = np.zeros(agru.size, dtype=int) == 0
    if flags[3]:
        lux = luz
        extra = 0
    else:
        lux = (luz / magnitud(luz)) * cnfgluz[2]
        extra = cnfgluz[2] - magnitud(np.array([mat[0], mat[0], mat[1]]))
    dep = np.argsort(np.sum(np.power(apos - lux, 2.0), axis=1))
    for d in range(dep.size - 1, -1, -1):
        dd = dep[d]
        if bias[dd]:
            bias[dd] = False
            bla, llego = rayoLuz(lux, pos[dd, :], apos, aacol, agru,
                                       zona, extra, bias, plim)
            for b in bla:
                milu[b[0]] = min(255, b[1] + milu[b[0]])
            milu[dd] = min(255, llego + milu[dd])
    if not maraton:
        cronometro("iluminacion")
    # difuminar las sombras
    bias = np.zeros(agru.size, dtype=int) == 0
    for u in range(bias.size):
        bias[u] = False
        bb = []
        for v in range(bias.size):
            if bias[v] and agru[u] == agru[v]:
                d = np.power(apos[u, :] - apos[v, :], 2.0).sum()
                if d <= cnfgluz[1]:
                    bb.append(v)
        slu = milu[u]
        for v in bb:
            slu += milu[v]
        slu /= len(bb) + 1
        milu[u] = (slu + milu[u]) / 2
        for v in bb:
            milu[v] = slu
    milu = milu * ((1 - cnfgluz[4]) / 255) + cnfgluz[4]
    if not maraton:
        cronometro("difuminacion")
    # dibujar los voxels
    ss = pg.Surface(mat, pg.SRCALPHA, 32)
    ss.fill((0, 0, 0, 0))
    s = pg.Surface((12, 12), pg.SRCALPHA, 32)
    dep = np.argsort(np.sum(np.power(apos - cam, 2.0), axis=1))
    if flags[4]:
        apos[:, 1] = np.subtract(apos[:, 1], apos[:, 2] * 0.5)
    else:
        apos[:, 1] = np.subtract(apos[:, 1], apos[:, 2])
    apos = apos[:, :2] + (cen - 6)
    for d in range(len(dep) - 1, -1, -1):
        dd = dep[d]
        s.fill((0, 0, 0, 0))
        c = aacol[dd, :] * np.array([milu[dd], milu[dd], milu[dd], 1], dtype=float)
        c = np.array(np.clip(c, 0, 255), dtype=int)
        pg.draw.circle(s, c, (6, 6), 5)
        dibuContorno(s, c)
        ss.blit(s, (apos[dd, 0], apos[dd, 1]))
    return ss

def dibujaGrupo():
    global pos
    global gru
    global mig
    global cam
    global cen
    global luz
    global mat
    global giro
    global flags
    ss = pg.Surface(mat, pg.SRCALPHA, 32)
    ss.fill((0, 0, 0, 0))
    s1, s2, sv = puntosTraslucidos()
    # poner luz y centro
    apos = pos.copy()
    agru = gru.copy()
    apos = np.append(apos, [luz], axis=0)
    apos = np.append(apos, [luz * np.array([1, 1, 0], dtype=float)], axis=0)
    agru = np.append(agru, -2)
    agru = np.append(agru, -2)
    apos = np.append(apos, [np.zeros(3)], axis=0)
    agru = np.append(agru, -3)
    www = (mat[0] / 2) * 0.9
    ooo = np.deg2rad(giro)
    apos = np.append(apos, [np.array([www * np.cos(ooo),
                                      www * np.sin(ooo), 0])], axis=0)
    agru = np.append(agru, -3)
    # dibujar los voxels
    if mig == -1:
        ggg = np.zeros(agru.size) == 0
    else:
        ggg = agru == mig
    dep = np.argsort(np.sum(np.power(apos - cam, 2.0), axis=1))
    if flags[4]:
        apos[:, 1] = np.subtract(apos[:, 1], apos[:, 2] * 0.5)
    else:
        apos[:, 1] = np.subtract(apos[:, 1], apos[:, 2])
    apos = apos[:, :2] + (cen - 6)
    for d in range(len(dep) - 1, -1, -1):
        dd = dep[d]
        if agru[dd] < -1:
            ss.blit(sv[agru[dd] + 3], (apos[dd, 0], apos[dd, 1]))
        elif ggg[dd]:
            ss.blit(s2, (apos[dd, 0], apos[dd, 1]))
        else:
            ss.blit(s1, (apos[dd, 0], apos[dd, 1]))
    return ss

def dibujaPlanos(eje, viejines=[]):
    global pos
    global gru
    global mig
    global cen
    global luz
    global mat
    global giro
    if eje == 0 or eje == 1:
        ss = pg.Surface((mat[0], mat[1] - mat[0] / 4), pg.SRCALPHA, 32)
        mcen = cen - 6
    else:
        ss = pg.Surface((mat[0], mat[0]), pg.SRCALPHA, 32)
        mcen = np.array([cen[0], cen[0]]) - 6
    ss.fill((0, 0, 0, 0))
    if len(viejines) == 0:
        s1, s2, sv = puntosTraslucidos()
        # poner luz y centro
        apos = pos.copy()
        agru = gru.copy()
        apos = np.append(apos, [luz], axis=0)
        agru = np.append(agru, -2)
        apos = np.append(apos, [np.zeros(3)], axis=0)
        agru = np.append(agru, -3)
        # dibujar los voxels
        apos = giroInt(apos, -giro)
        if mig == -1:
            ggg = np.zeros(agru.size) == 0
        else:
            ggg = agru == mig
        viejines = [s1, s2, sv, apos, agru, ggg]
    else:
        s1 = viejines[0]
        s2 = viejines[1]
        sv = viejines[2]
        apos = viejines[3]
        agru = viejines[4]
        ggg = viejines[5]
    if eje == 0:
        dep = np.argsort(-apos[:, 0])
        for d in range(len(dep) - 1, -1, -1):
            dd = dep[d]
            if agru[dd] < -1:
                ss.blit(sv[agru[dd] + 3], (-apos[dd, 1],
                                           -apos[dd, 2]) + mcen)
            elif ggg[dd]:
                ss.blit(s2, (-apos[dd, 1], -apos[dd, 2]) + mcen)
            else:
                ss.blit(s1, (-apos[dd, 1], -apos[dd, 2]) + mcen)
    elif eje == 1:
        dep = np.argsort(-apos[:, 1])
        for d in range(len(dep) - 1, -1, -1):
            dd = dep[d]
            if agru[dd] < -1:
                ss.blit(sv[agru[dd] + 3], (apos[dd, 0],
                                           -apos[dd, 2]) + mcen)
            elif ggg[dd]:
                ss.blit(s2, (apos[dd, 0], -apos[dd, 2]) + mcen)
            else:
                ss.blit(s1, (apos[dd, 0], -apos[dd, 2]) + mcen)
    else:
        dep = np.argsort(-apos[:, 2])
        for d in range(len(dep) - 1, -1, -1):
            dd = dep[d]
            if agru[dd] < -1:
                ss.blit(sv[agru[dd] + 3], (apos[dd, 0],
                                           apos[dd, 1]) + mcen)
            elif ggg[dd]:
                ss.blit(s2, (apos[dd, 0], apos[dd, 1]) + mcen)
            else:
                ss.blit(s1, (apos[dd, 0], apos[dd, 1]) + mcen)
    return ss, viejines

def borraPlanos():
    surf = pg.display.get_surface()
    tll = surf.get_size()
    tll = (int(tll[0] / 2), tll[1])
    sss = pg.Surface(tll, pg.SRCALPHA, 32)
    sss.fill((0, 0, 0, 255))
    surf.blit(sss, (tll[0], 0))
    pg.display.flip()

def galeriaTexturas():
    global ecol
    global shadow
    ecol.append(["sombra", [shadow, shadow, shadow]])
    c1 = np.array([242, 82, 53, 255], dtype=int)
    c2 = np.array([240, 49, 15, 255], dtype=int)
    c3 = np.array([191, 39, 13, 255], dtype=int)
    ecol.append(["rojo", [c1, c2, c3]])
    c1 = np.array([251, 170, 89, 255], dtype=int)
    c2 = np.array([250, 143, 37, 255], dtype=int)
    c3 = np.array([238, 122, 6, 255], dtype=int)
    ecol.append(["naranja", [c1, c2, c3]])
    c1 = np.array([240, 237, 94, 255], dtype=int)
    c2 = np.array([236, 232, 53, 255], dtype=int)
    c3 = np.array([211, 207, 20, 255], dtype=int)
    ecol.append(["amarillo", [c1, c2, c3]])
    c1 = np.array([112, 189, 100, 255], dtype=int)
    c2 = np.array([88, 177, 75, 255], dtype=int)
    c3 = np.array([74, 149, 64, 255], dtype=int)
    ecol.append(["verde", [c1, c2, c3]])
    c1 = np.array([82, 239, 78, 255], dtype=int)
    c2 = np.array([33, 234, 28, 255], dtype=int)
    c3 = np.array([22, 199, 18, 255], dtype=int)
    ecol.append(["limon", [c1, c2, c3]])
    c1 = np.array([62, 62, 62, 255], dtype=int)
    c2 = np.array([74, 74, 74, 255], dtype=int)
    c3 = np.array([40, 40, 40, 255], dtype=int)
    ecol.append(["negro", [c1, c2, c3]])
    c1 = np.array([126, 126, 126, 255], dtype=int)
    c2 = np.array([110, 110, 110, 255], dtype=int)
    c3 = np.array([148, 148, 148, 255], dtype=int)
    ecol.append(["gris", [c1, c2, c3]])
    c1 = np.array([211, 211, 211, 255], dtype=int)
    c2 = np.array([229, 229, 229, 255], dtype=int)
    c3 = np.array([188, 188, 188, 255], dtype=int)
    ecol.append(["blanco", [c1, c2, c3]])
    c1 = np.array([116, 90, 63, 255], dtype=int)
    c2 = np.array([89, 70, 49, 255], dtype=int)
    c3 = np.array([136, 106, 74, 255], dtype=int)
    ecol.append(["cafe", [c1, c2, c3]])
    c1 = np.array([208, 185, 130, 255], dtype=int)
    c2 = np.array([193, 163, 89, 255], dtype=int)
    c3 = np.array([170, 138, 64, 255], dtype=int)
    ecol.append(["caqui", [c1, c2, c3]])
    c1 = np.array([31, 100, 203, 255], dtype=int)
    c2 = np.array([62, 128, 225, 255], dtype=int)
    c3 = np.array([104, 155, 232, 255], dtype=int)
    ecol.append(["azul", [c1, c2, c3]])
    c1 = np.array([53, 53, 236, 255], dtype=int)
    c2 = np.array([22, 22, 233, 255], dtype=int)
    c3 = np.array([90, 90, 239, 255], dtype=int)
    ecol.append(["marino", [c1, c2, c3]])
    c1 = np.array([53, 217, 230, 255], dtype=int)
    c2 = np.array([91, 237, 244, 255], dtype=int)
    c3 = np.array([14, 200, 209, 255], dtype=int)
    ecol.append(["agua", [c1, c2, c3]])
    c1 = np.array([202, 43, 198, 255], dtype=int)
    c2 = np.array([174, 36, 171, 255], dtype=int)
    c3 = np.array([216, 65, 211, 255], dtype=int)
    ecol.append(["morado", [c1, c2, c3]])
    c1 = np.array([248, 152, 192, 255], dtype=int)
    c2 = np.array([245, 126, 177, 255], dtype=int)
    c3 = np.array([243, 90, 155, 255], dtype=int)
    ecol.append(["rosa", [c1, c2, c3]])
    c1 = np.array([243, 136, 39, 255], dtype=int)
    c2 = np.array([58, 33, 33, 255], dtype=int)
    c3 = np.array([67, 46, 24, 255], dtype=int)
    ecol.append(["halloween", [c1, c2, c3]])
    c1 = np.array([62, 168, 67, 255], dtype=int)
    c2 = np.array([168, 220, 58, 255], dtype=int)
    c3 = np.array([239, 65, 39, 255], dtype=int)
    ecol.append(["navidad", [c1, c2, c3]])
    c1 = np.array([191, 191, 191, 255], dtype=int)
    c2 = np.array([168, 168, 168, 255], dtype=int)
    c3 = np.array([51, 51, 51, 255], dtype=int)
    ecol.append(["mimo", [c1, c2, c3]])
    c1 = np.array([245, 114, 16, 255], dtype=int)
    c2 = np.array([43, 91, 219, 255], dtype=int)
    c3 = np.array([50, 238, 23, 255], dtype=int)
    ecol.append(["payaso", [c1, c2, c3]])
    c1 = np.array([236, 231, 26, 255], dtype=int)
    c2 = np.array([208, 204, 17, 255], dtype=int)
    c3 = np.array([142, 69, 45, 255], dtype=int)
    ecol.append(["leopardo", [c1, c2, c3]])
    c1 = np.array([57, 120, 54, 255], dtype=int)
    c2 = np.array([96, 142, 32, 255], dtype=int)
    c3 = np.array([163, 122, 67, 255], dtype=int)
    ecol.append(["reptil", [c1, c2, c3]])
    c1 = np.array([154, 65, 207, 255], dtype=int)
    c2 = np.array([103, 41, 231, 255], dtype=int)
    c3 = np.array([249, 23, 243, 255], dtype=int)
    ecol.append(["saurio", [c1, c2, c3]])
    c1 = np.array([153, 251, 245, 100], dtype=int)
    c2 = np.array([190, 252, 249, 100], dtype=int)
    c3 = np.array([115, 249, 242, 100], dtype=int)
    ecol.append(["vidrio", [c1, c2, c3]])
    c1 = np.array([130, 126, 165, 255], dtype=int)
    c2 = np.array([0, 0, 0, 0], dtype=int)
    c3 = np.array([0, 0, 0, 0], dtype=int)
    ecol.append(["malla", [c1, c2, c3]])
    c1 = np.array([108, 85, 79, 255], dtype=int)
    c2 = np.array([121, 114, 85, 255], dtype=int)
    c3 = np.array([0, 0, 0, 0], dtype=int)
    ecol.append(["reja", [c1, c2, c3]])
    c1 = np.array([77, 141, 61, 255], dtype=int)
    c2 = np.array([153, 199, 107, 100], dtype=int)
    c3 = np.array([131, 248, 114, 50], dtype=int)
    ecol.append(["hojas", [c1, c2, c3]])
    unicaTextura()

def brochaEsfera(des, rad, inv):
    global gru
    global pos
    global col
    global flags
    if gru.size > 0:
        agiro = giraCentro() if flags[2] else 0
        ggg = mascara()
        dmin = np.power(rad, 2.0)
        for u in range(gru.size - 1, -1, -1):
            if ggg[u]:
                d = np.power(pos[u, :] - des, 2.0).sum()
                if (d <= dmin) != inv:
                    col[u, :] = pintar()
        giraTodo(agiro)

def brochaCaja(des1, des2, inv):
    global gru
    global pos
    global col
    global flags
    if gru.size > 0:
        agiro = giraCentro() if flags[2] else 0
        ggg = mascara()
        for u in range(gru.size - 1, -1, -1):
            if ggg[u]:
                if not (False in (pos[u, :] >= des1) or
                        False in (pos[u, :] <= des1 + des2)) != inv:
                    col[u, :] = pintar()
        giraTodo(agiro)

def brochaCilindro(des, rad, alt, eje, inv):
    global gru
    global pos
    global col
    global flags
    if gru.size > 0:
        agiro = giraCentro() if flags[2] else 0
        ggg = mascara()
        dmin = np.power(rad, 2.0)
        if eje == 0:
            for u in range(gru.size - 1, -1, -1):
                if ggg[u]:
                    bor = False
                    if inv:
                        if pos[u, 0] < des[0] or pos[u, 0] > des[0] + alt:
                            bor = True
                        else:
                            d = np.power(pos[u, 1:3] - des[1:3], 2.0).sum()
                            if d > dmin:
                                bor = True
                    else:
                        if pos[u, 0] >= des[0] and pos[u, 0] <= des[0] + alt:
                            d = np.power(pos[u, 1:3] - des[1:3], 2.0).sum()
                            if (d <= dmin) != inv:
                                bor = True
                    if bor:
                        col[u, :] = pintar()
        elif eje == 1:
            for u in range(gru.size - 1, -1, -1):
                if ggg[u]:
                    bor = False
                    if inv:
                        if pos[u, 1] < des[1] and pos[u, 1] > des[1] + alt:
                            bor = True
                        else:
                            d = np.power(pos[u, 0:3:2] - des[0:3:2], 2.0).sum()
                            if d > dmin:
                                bor = True
                    else:
                        if pos[u, 1] >= des[1] and pos[u, 1] <= des[1] + alt:
                            d = np.power(pos[u, 0:3:2] - des[0:3:2], 2.0).sum()
                            if d <= dmin:
                                bor = True
                    if bor:
                        col[u, :] = pintar()
        else:
            for u in range(gru.size - 1, -1, -1):
                if ggg[u]:
                    bor = False
                    if inv:
                        if pos[u, 2] < des[2] and pos[u, 2] > des[2] + alt:
                            bor = True
                        else:
                            d = np.power(pos[u, :2] - des[:2], 2.0).sum()
                            if d > dmin:
                                bor = True
                    else:
                        if pos[u, 2] >= des[2] and pos[u, 2] <= des[2] + alt:
                            d = np.power(pos[u, :2] - des[:2], 2.0).sum()
                            if d <= dmin:
                                bor = True
                    if bor:
                        col[u, :] = pintar()
        giraTodo(agiro)

def brochaAzar(porc):
    global gru
    global pos
    global col
    if gru.size > 0:
        ggg = mascara()
        des, base, mas = masaCentro(False)
        bias = np.zeros(gru.size, dtype=int) == 0
        repit = int(np.floor(mas * porc))
        for r in range(repit):
            while True:
                u = np.random.randint(0, gru.size, 1)[0]
                if ggg[u] and bias[u]:
                    col[u, :] = pintar()
                    bias[u] = False
                    break
        verificarGrupos()

def filtroColor():
    global gru
    global pos
    global col
    global cnfgluz
    bias = np.zeros(gru.size, dtype=int) == 0
    ggg = mascara()
    for u in range(bias.size):
        bias[u] = False
        if ggg[u]:
            bb = []
            for v in range(bias.size):
                if bias[v] and ggg[v]:
                    d = np.power(pos[u, :] - pos[v, :], 2.0).sum()
                    if d <= cnfgluz[1]:
                        bb.append(v)
            ccc = col[u, :]
            for v in bb:
                ccc += col[v, :]
            ccc = np.clip(np.array(ccc / (len(bb) + 1), dtype=int), 0, 255)
            col[u, :] = ccc
            for v in bb:
                col[v, :] = ccc

def pintarLuz():
    global luz
    global pos
    global col
    global gru
    global cnfgluz
    global mat
    global flags
    if gru.size > 0:
        agiro = giraCentro() if flags[2] else 0
        ggg = mascara()
        agru, zona, plim = zonificarGeneral()
        colis = np.zeros(agru.size, dtype=int) == 1
        bias = ggg.copy()
        if flags[3]:
            lux = luz
            extra = 0
        else:
            lux = (luz / magnitud(luz)) * cnfgluz[2]
            extra = cnfgluz[2] - magnitud(np.array([mat[0], mat[0], mat[1]]))
        dep = np.argsort(np.sum(np.power(pos - lux, 2.0), axis=1))
        for d in range(dep.size - 1, -1, -1):
            dd = dep[d]
            if bias[dd] and not colis[dd]:
                impac = rayoColision(lux, pos[dd, :], agru, zona, extra, bias, plim)
                if impac == -1:
                    colis[dd] = True
                else:
                    colis[impac] = True
        for u in range(gru.size - 1, -1, -1):
            if colis[u]:
                col[u, :] = pintar()
        giraTodo(agiro)

def efectoColor(tipo):
    global col
    global gru
    global acol
    ggg = mascara()
    # escala de grises
    if tipo == 0:
        for u in range(gru.size):
            if ggg[u]:
                col[u, :3] = col[u, :3].mean()
    # blanco y negro
    elif tipo == 1:
        for u in range(gru.size):
            if ggg[u]:
                col[u, :3] = col[u, :3].mean()
                if col[u, 0] > 128:
                    col[u, :3] = np.array([205, 205, 205], dtype=int)
                else:
                    col[u, :3] = np.array([50, 50, 50], dtype=int)
    # negativo
    elif tipo == 2:
        for u in range(gru.size):
            if ggg[u]:
                col[u, :3] = np.array([255, 255, 255], dtype=int) - col[u, :3]
    # promedio con color seleccionado
    elif tipo == 3:
        for u in range(gru.size):
            if ggg[u]:
                col[u, :3] = np.array((col[u, :3] + pintar()[:3]) / 2, dtype=int)
    # variar color al azar
    elif tipo == 4:
        for u in range(gru.size):
            if ggg[u]:
                otro = np.random.randint(-50, 50, 3, dtype=int)
                col[u, :3] = np.clip(col[u, :3] + otro, 0, 255)
    # color al azar pero monotono
    elif tipo == 5:
        c = np.random.randint(0, 256, 3, dtype=int)
        for u in range(gru.size):
            if ggg[u]:
                col[u, :3] = np.clip(c + np.random.randint(-50, 50, 3,
                                                           dtype=int), 0, 255)
    # color al azar total los 3
    elif tipo == 6:
        for u in range(gru.size):
            if ggg[u]:
                col[u, :3] = np.random.randint(0, 256, 3, dtype=int)
    # nuevo color a color similar
    elif tipo == 7:
        sens = 12
        aacol = acol.copy()
        elegirTextura(input(tab() + "nombre textura: "))
        vie = acol
        acol = aacol
        for u in range(gru.size):
            if ggg[u]:
                if (np.sum(vie[0] >= col[u, :] - sens) == 4 and
                        np.sum(vie[0] <= col[u, :] + sens) == 4):
                    col[u, :] = pintar()
                elif (np.sum(vie[1] >= col[u, :] - sens) == 4 and
                      np.sum(vie[1] <= col[u, :] + sens) == 4):
                    col[u, :] = pintar()
                elif (np.sum(vie[2] >= col[u, :] - sens) == 4 and
                      np.sum(vie[2] <= col[u, :] + sens) == 4):
                    col[u, :] = pintar()

def pintarSombra():
    global col
    global acol
    global gru
    global cnfgluz
    aacol = acol.copy()
    ancol = col.copy()
    bla = np.array([255, 255, 255, 255], dtype=int)
    nuevoColor(np.array([0, 0, 0, 255], dtype=int), bla, bla)
    pintarGrupo()
    nuevoColor(bla, bla, bla)
    cronometro("", False)
    pintarLuz()
    cronometro("iluminacion")
    filtroColor()
    cronometro("difuminacion")
    acol = aacol
    ggg = mascara()
    fu = cnfgluz[5] / 255
    milu = col[:, 0] * fu * ((1 - cnfgluz[4]) / 255) + cnfgluz[4]
    for u in range(gru.size):
        if ggg[u]:
            c = ancol[u, :3] * np.array([milu[u], milu[u], milu[u]],
                                        dtype=float)
            col[u, :3] = np.array(np.clip(c, 0, 255), dtype=int)
            col[u, 3] = ancol[u, 3]
        else:
            col[u, :] = ancol[u, :]

# funciones de animacion

def nuevaAnimacion(nombre, ani):
    global libro
    if len(nombre) > 0:
        ind = -1
        for a in range(len(libro)):
            if libro[a][0] == nombre:
                ind = a
                break
        if ind == -1:
            libro.append([nombre, ani])
        else:
            libro[ind] = [nombre, ani]

def verAnimaciones():
    global libro
    print("***Animaciones***")
    for a in libro:
        print(tab() + a[0])

def eliminarAnimacion(nombre):
    global libro
    if nombre == "-1":
        libro = []
        print(tab() + "Ok")
    else:
        for a in range(len(libro) - 1, -1, -1):
            if libro[a][0] == nombre:
                libro.pop(a)
                print(tab() + "Ok")

def elegirAnimacion(nombre):
    global libro
    ani = [False]
    ok = False
    for a in libro:
        if a[0] == nombre:
            ani = a[1]
            ok = True
            break
    return ani, ok

main()

"""
Tareas:
config
- exportar opcion solo sombras, no en animacion
- guardar y abrir animaciones del txt
- verificar tipos de renderizado, zonas, azar, completo
- ver color actual y de mouse en GUI
ani
- poder ejecutar animacion sin exportar
- animacion transparente mas o menos
- animacion visible uno por uno
- animacion de destruccion por particulas al azar
- animacion de cambio de color para un grupo o todo
- animacion de respiracion idle para grupo
- animacion de pies para grupos de pies
- animacion de particulas para un grupo o todo
- animacion particulas sifon, atrae o repele tipo PSO
- animacion particulas torcion tornado
- animacion de caida solo para un grupo o todo (ya)
- animacion escala
- animacion de rotacion
- animacion de movimiento
- animacion de color moviendose en grupo
- animacion de rotacion solo de iluminacion
tool
- 
crear
- 
col
- 
ext
- mediciones con mouse
- obtener color de paleta GUI con mouse
- acciones manuales, con mouse
- hacer ayuda pdf
- abrir txt con blender, godot o unity
- convertir modelo blender en puntos y luego en txt
mejorar
- 
"""
