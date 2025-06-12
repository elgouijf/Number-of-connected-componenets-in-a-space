#!/usr/bin/env python3
"""
compute sizes of all connected components.
sort and display.
Optimized version
"""

from sys import argv
from geo.point import Point
from collections import deque, defaultdict

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

def points_sont_proches(p1, p2, d_seuil):
    """
    Retourne True si et seulement si la distance entre p1 et p2 
    est inférieure ou égale à la distance seuil.
    """
    dx, dy = p1.coordinates[0] - p2.coordinates[0], p1.coordinates[1] - p2.coordinates[1]
    return (dx * dx) + (dy * dy) <= (d_seuil * d_seuil)           # L'opérateur sqrt étant couteux, on recourt
                                                                  # plutôt à une comparaison de distances carrées

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
        grille[creer_cellule_point(point, d_min)].append(point)
    return grille


def trouver_voisins_directs_potentiels(point, grille, d_min):
    """ Renvoie la liste des points correspondant aux cellules adjacentes
    à celle de 'point' et pouvant être voisin de 'point' """
    voisins = []
    cell_x, cell_y = creer_cellule_point(point, d_min)

    # Recherche dans 9 cellules adjacentes( y compris la cellule de 'point')
    for c_x, c_y in ((-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (1,1), (-1,-1), (1,-1), (-1,1)):
        voisins.extend(grille.get((cell_x + c_x, cell_y + c_y), []))
    return voisins 


def construire_graphe(points, distance_seuil):
    """
    Construit et retourne le graphe G = (V, E) où V est l'ensemble des sommets (points) et E l'ensemble des arêtes.
    Une arête existe entre deux points si et seulement s'ils sont proches au sens de la fonction 
    points_sont_proches. (version optimisée <-> bonne gestion des arêtes)
    """
    sommets = set(points) 
    aretes = {point: [] for point in points}
    grille = creer_grille(points, distance_seuil)

    for point in points:
        for voisin in trouver_voisins_directs_potentiels(point, grille, distance_seuil):
            if voisin in sommets and points_sont_proches(point, voisin, distance_seuil):
                aretes[point].append(voisin)
    return sommets, aretes


def explorer_composante_connexe(point, graphe):
    """
    Explore une composante connexe itérativement en supprimant de l'ensemble des sommets
    tout sommet qui aura été détecté comme faisant partie de la composante connexe à laquelle
    appartient 'point'.
    """
    sommets, aretes = graphe
    pile = deque([point])
    sommets.remove(point)               # Suppression directe de 'point' de l'ensmeble des sommets => éviter de vérifier si 'point' est traîté ou pas.
                                        # Utile aussi dans la fonctin print_components_sizes qui n'aura plus à vérifier si un sommet est marqué (car il a été supprimé)
    taille = 1 

    while pile:
        point_courant = pile.pop() 
        for voisin in aretes[point_courant]:
            if voisin in sommets:
                sommets.remove(voisin)
                pile.append(voisin)
                taille += 1 
    return taille


def print_components_sizes(distance_seuil, points):
    """
    Affichage des tailles (ie nombre de sommets) triées dans l'ordre décroissant
    des composantes connexes.
    """
    graphe = construire_graphe(points, distance_seuil)
    sommets, _ = graphe
    tailles = []

    while sommets:
        point = next(iter(sommets))
        tailles.append(explorer_composante_connexe(point, graphe))

    tailles.sort(reverse=True) 
    print(tailles)


def main():
    """
    ne pas modifier: on charge une instance et on affiche les tailles
    """
    for instance in argv[1:]:
        distance, points = load_instance(instance)
        print_components_sizes(distance, points)

main()

