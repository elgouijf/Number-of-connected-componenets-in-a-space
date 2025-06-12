#!/usr/bin/env python3
"""
compute sizes of all connected components.
sort and display.
"""

from sys import argv
from geo.point import Point
from collections import defaultdict

# "Tokens" pour l'état des points
PAS_ENCORE_TRAITE = 0                     # Pour les points ne faisant pas partie d'une composante connexe.
DANS_COMPOSANTE_CONNEXE = 1               # Pour les points faisant partie d'une composante connexe.

def load_instance(filename):
    """
    loads .pts file.
    returns distance limit and points.
    """
    with open(filename, "r") as instance_file:
        lines = iter(instance_file)
        distance = float(next(lines))
        points = [Point([float(f) for f in l.split(",")]) for l in lines]

    return distance, points


def points_sont_proches(p1, p2, distance_seuil):
    """
    Retourne True si et seulement si la distance entre p1 et p2 
    est inférieure ou égale à la distance seuil.
    """
    return p1.distance_to(p2) <= distance_seuil

def creer_cellule_point(point, d_min):
    """ Crée et renvoie une cellule carrée de coordonnées i,j et de coté d_min
    correspondant au point 'point' """
    x,y = point.coordinates
    i = int(x // d_min)
    j = int(y // d_min)
    return (i, j)


def creer_grille(points, d_min):
    """ Crée et renvoie une grille faite de cellules créées
    par la fonction creer_cellule_point """
    grille = defaultdict(list)
    for point in points:
        cellule = creer_cellule_point(point, d_min)
        grille[cellule].append(point)
    return grille


def trouver_voisins_directs_potentiels(point, grille , d_min):
    """ Renvoie la liste des points correspondant aux cellules adjacentes
     à celle de 'point' et pouvant être voisin de 'point' """
    voisins_potentiels = []
    cellule = creer_cellule_point(point,d_min)
    for cell_x in (-1,0,1):                         # Les cellules adjacentes se trouvent dans la sous-grille carrée
        for cell_y in (-1,0,1):                     # de côté 3d_min dont le centre est la cellule 'cellule
            c_x = cellule[0] + cell_x
            c_y = cellule[1] + cell_y
            if (c_x ,c_y) in grille :
                voisins_potentiels += (grille[(c_x, c_y)])
    return voisins_potentiels


def construire_graphe(points, distance_seuil):
    """
    Construit et retourne le graphe G = (V, E) où V est l'ensemble des sommets (points) et E l'ensemble des arêtes.
    Une arête existe entre deux points si et seulement s'ils sont proches au sens de la fonction 
    points_sont_proches.
    """
    sommets = {point: PAS_ENCORE_TRAITE for point in points}        # Initialisation du token de tous les points à "pas_encore_traité".
    aretes = {point: [] for point in sommets}                       # Initialisation des arêtes de la façon suivante : à chaque
                                                                    # point est associé une liste vide dans laquelle seront stockés 
                                                                    # les points qui lui sont proches.
    grille = creer_grille(points, distance_seuil)
    for point in points:
        voisins_potentiels = trouver_voisins_directs_potentiels(point, grille, distance_seuil)
        for voisin in voisins_potentiels :
            if points_sont_proches(voisin, point, distance_seuil) :
                aretes[point].append(voisin)
                #aretes[voisin].append(point)        ne change rien  à un certain moment
                                                # voisin lui même va être traité comme 'point' => éviter les doublons dans aretes
                                                # quoique ça (existence des doublons) n'influence pas le calcul des tailles grâce au marquage avec les tokens dans sommets (et non dans aretes)
    return (sommets, aretes)



def explorer_composante_connexe(point, graphe):
    """
    Explore une composante connexe itérativement en marquant les sommets avec 
    le token "dans_composante_connexe".
    """
    taille_composante = 0
    sommets, aretes = graphe
    pile = [point]                                                  # La pile contient au début le "premier" sommet de la composante connexe à explorer
    sommets[point] = DANS_COMPOSANTE_CONNEXE                        # On marque ce sommet (point) comme faisant partie d'une composante connexe.
    while pile:
        point_courant = pile.pop()
        taille_composante += 1
        for voisin in aretes[point_courant]:                        # Les voisins de ce sommet (ie sommets qui y sont liés via une arête) appartiennent aussi
                                                                    # à la composante connexe.
            if sommets[voisin] == PAS_ENCORE_TRAITE:
                sommets[voisin] = DANS_COMPOSANTE_CONNEXE           # On marque les voisins comme faisant partie d'une composante connexe
                pile.append(voisin)                                 # et on les empile dans la pile des sommets dont les voisins doivent aussi 
                                                                    # être marqués comme faisant partie d'une composante connexe.
    return taille_composante

def explorer_composante_connexe_rec(point, graphe, taille_composante):
    """
    Explore une composante connexe récursivement à partir d'un certain sommet (point)
    """
    sommets, aretes = graphe

    sommets[point] = DANS_COMPOSANTE_CONNEXE                        # On marque ce point comme faisant partie d'une composante connexe.
    taille_composante[0] += 1                                       # Incrémentation de la taille de la composante connexe courante (suite à l'ajout du sommet "point").

    for neighbor in aretes[point]:                                  # Là, on explore tous les sommets voisins qui ne font toujours pas partie d'une composante connexe.
        if sommets[neighbor] == PAS_ENCORE_TRAITE :
            explorer_composante_connexe_rec(neighbor, graphe, taille_composante)


def print_components_sizes(distance_seuil, points):
    """
    Affichage des tailles (ie nombre de sommets) triées dans l'ordre décroissant
    des composantes connexes.
    """
    graphe = construire_graphe(points, distance_seuil)
    sommets, _ = graphe
    tailles_composantes_connexes = []

    for point in sommets :
        if sommets[point] == DANS_COMPOSANTE_CONNEXE:                            # On ignore les sommets faisant déjà partie d'une composante connexe.
            continue                                     
        taille_composante_courante = explorer_composante_connexe(point, graphe)
        # explorer_composante_connexe_rec(point, graphe, taille_composante_courante)
        tailles_composantes_connexes.append(taille_composante_courante)       # On stocke la taille de la composante connexe courante.

    tailles_composantes_connexes.sort(reverse=True)                              # Mise en ordre décroissant des tailles des composantes connexes.
    print(tailles_composantes_connexes)          


def main():
    """
    ne pas modifier: on charge une instance et on affiche les tailles
    """
    for instance in argv[1:]:
        distance, points = load_instance(instance)
        print_components_sizes(distance, points)


main()