import itertools
import numpy as np
import Bio.PDB


def get_distance(coords1, coords2):
    superimposer = Bio.PDB.Superimposer()
    superimposer.set_atoms(coords1, coords2)
    return superimposer.rms


def get_distance_matrix(ensemble1, ensemble2):
    all_atoms = [list(structure.get_atoms()) for structure in itertools.chain(ensemble1, ensemble2)]
    n = len(all_atoms)

    distance_matrix = np.zeros((n, n), dtype=np.float_)
    for i, j in itertools.combinations(range(n), 2):
        distance_matrix[i, j] = distance_matrix[j, i] = get_distance(all_atoms[i], all_atoms[j])

    return distance_matrix


def directed_distance(distance_matrix, weights1, weights2, reversed=False):
    min_distaces = []
    for i in range(len(weights1)):
        distances = []
        for j in range(len(weights2)):
            if reversed:
                distances.append((distance_matrix[len(weights2) + i, j], i, j))
            else:
                distances.append((distance_matrix[i, len(weights1) + j], i, j))
        min_distaces.append(min(distances))

    weighted_distances = [(dist * weights1[i] * weights2[j], dist, i, j) for dist, i, j in min_distaces]
    return max(weighted_distances)


def hausdorff_distance(distance_matrix, weights1, weights2):
    _, final_distance1, i1, j1 = directed_distance(distance_matrix, weights1, weights2)
    _, final_distance2, j2, i2 = directed_distance(distance_matrix, weights2, weights1, reversed=True)

    if final_distance1 > final_distance2:
        return final_distance1, (i1, j1)
    else:
        return final_distance2, (i2, j2)


def compare_ensembles(files1, files2, weights1, weights2):
    pdb_parser = Bio.PDB.PDBParser(QUIET=True)
    structures1, structures2 = [], []
    for i, file in enumerate(files1):
        structures1.append(pdb_parser.get_structure(str(i), file))

    for i, file in enumerate(files2):
        structures2.append(pdb_parser.get_structure(str(i), file))

    distance_matrix = get_distance_matrix(structures1, structures2)

    return hausdorff_distance(distance_matrix, weights1, weights2)[0]
