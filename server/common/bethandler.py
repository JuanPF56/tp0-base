
class BetHandler(multiprocessing.Process):
    def __init__(self, 



    def join(self):
        """
        Join process
        """
        self.joined = True
        super().join()