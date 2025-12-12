from lib.config.ConfigParser import ConfigParser
from lib.processing.Executor import Executor

def assignment471(config):
    """
    @author: Gerrald
    @date: 10-12-2025
    """
    executor = Executor("samples\\stethoscope_2_realHeart_", config, True)
    executor.execute()
    executor.summarize()

def main():
    """
    @author: Gerrald
    @date: 10-12-2025

    The main loop. Can be changed to choose whether to run assignment 4.2.2 or 4.2.3.
    
    """
    config = ConfigParser()
    assignment471(config)

if __name__ == "__main__":
    main()