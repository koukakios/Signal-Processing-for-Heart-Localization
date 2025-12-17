import numpy as np

def a_z(s_position, mic_positions, M, v, f0):

    result = []

    for microphone in mic_positions:
        rm = np.linalg.norm(s_position - microphone)
        tm = rm/v
        result.append( (np.exp(-1j * 2*np.pi*f0 * tm) ) / rm)

   
    result = np.array(result)
    return result
    


def music_z(Rx, Q, M, xyz_points, v, f0, mic_positions):
    
    eigenvals, eigenvecs = np.linalg.eigh(Rx)
    noises = M - Q
    Un = eigenvecs[:, :noises]

    result = []
    for candidate_source_location in xyz_points:
        
        a = a_z(candidate_source_location, mic_positions, M, v, f0)

        to_append = np.matmul(a.conj().T, Un)
        to_append = np.matmul(to_append, Un.conj().T)
        to_append = np.matmul(to_append, a)
        result.append(to_append)

    result = np.array([1 / result[i] for i in range (len(result)) ])

    return result


def mvdr_z(Rx, M, xyz_points, v, f0, mic_positions):
    
    
    result = []
    for candidate_source_location in xyz_points:
        a = a_z(candidate_source_location, mic_positions, M, v, f0)

        to_append = np.matmul(a.conj().T, np.linalg.inv(Rx))
        to_append = np.matmul(to_append, a)
        result.append(1/to_append)

    result = np.array([1 / result[i] for i in range (len(result)) ])

    return result



