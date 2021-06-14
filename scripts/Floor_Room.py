#Idea para obtener puntos varios de la superficie superior de UN SOLO SUELO

fase = [a for a in doc.Phases][-1]

def baricentro(a,b,c):
    #Calcula el baricentro de un triángulo
    #Le sumamos 3 pies (~1 metro) a la Z para que caiga en la habitación
    return XYZ((a.X+b.X+c.X)/3,(a.Y+b.Y+c.Y)/3,(a.Z+b.Z+c.Z)/3 + 3)

def floor_room(suelo, fase):
    #El proceso de siempre para encontrar la cara superior
    geometria = suelo.get_Geometry(Options())
    solidos = [s for s in geometria]
    solido = solidos[0]
    caras = [c for c in solido.Faces]
    for cara in caras:
        if cara.FaceNormal.Z > 0.97:
            cara_sup = cara
            break
    #Convertimos la cara en una malla y triangulamos
    malla = cara_sup.Triangulate(0)
    num = malla.NumTriangles
    for idx in range(num):
        #Vamos sacando baricentros de triángulos hasta que alguno esté en una room
        triangulo = malla.Triangle[idx]
        a, b, c = triangulo.Vertex[0], triangulo.Vertex[1], triangulo.Vertex[2]
        bar = baricentro(a,b,c)
        room = doc.GetRoomAtPoint(bar,fase)
        if room:
            return room
    #Si una vez recorridos todos los triángulos no sale ninguna habitación, devolvemos None
    return None
