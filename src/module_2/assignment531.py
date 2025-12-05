import numpy as np
from lib.config.ConfigParser import ConfigParser



valve_locs = {"M":np.array((6.37,10.65,6.00)),
              "T":np.array((0.94,9.57,5.5)),
              "A":np.array((5.5,11.00,3.6)),
              "P":np.array((3.9,11.5,4.5))}

valve_locs = np.array([(6.37,10.65,6.00), # M
              (0.94,9.57,5.5), # T
              (5.5,11.00,3.6), # A
              (3.9,11.5,4.5)]) # P

mic_locs = {0: np.array((2.5, 5, 0)),
            1: np.array((2.5, 10, 0)),
            2: np.array((2.5, 15, 0)),
            3: np.array((7.5, 5, 0)),
            4: np.array((7.5, 10, 0)),
            5: np.array((7.5, 15, 0))}

mic_locs = np.array([(2.5, 5, 0), # 0
            (2.5, 10, 0), # 1
            (2.5, 15, 0), # 2
            (7.5, 5, 0), # 3
            (7.5, 10, 0), # 4
            (7.5, 15, 0)]) # 5

# for i in range(6):
#     mic_locs[i] = (2.5+(i//3)*5,(i%3)*5+5,0))





def threeD_model():
    config = ConfigParser()
    
    
    
    
    
    for mic_loc in mic_locs:
        new_mic_loc = np.tile(mic_loc,(4,1)) # repeat the mic loc, to comply with the dimensions of np.linalg.norm
        
        dists_to_valves = np.linalg.norm(valve_locs-new_mic_loc, axis=1)
        
        # calc delays and gains using distances to the valves
        delays = dists_to_valves/config.Multichannel.V_body
        gains = 1/dists_to_valves
        # normalized the gains
        gains_normalized = gains/max(gains)
        
        
        
        print(delays,gains_normalized)
        break


if __name__ == "__main__":
    threeD_model()