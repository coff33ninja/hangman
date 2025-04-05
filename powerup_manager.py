# powerup_manager.py

class PowerUpManager:

    def __init__(self):

        """

        Initialize power-up counts.

        """

        self.power_ups = {"reveal_letter": 1, "extra_attempt": 1}



    def use_power_up(self, power_up, game):

        """

        Use a power-up if available. Returns True if successful, False otherwise.

        """

        if self.power_ups.get(power_up, 0) <= 0:

            return False

        if power_up == "reveal_letter":

            hint = game.provide_hint()

            if hint:

                self.power_ups[power_up] -= 1

                return True

        elif power_up == "extra_attempt":

            game.attempts_left += 1

            self.power_ups[power_up] -= 1

            return True

        return False



    def reset_power_ups(self):

        """

        Reset power-up counts to their initial values.

        """

        self.power_ups = {"reveal_letter": 1, "extra_attempt": 1}  # Reset to initial values



    def get_power_up_status(self):

        """

        Return the current status of power-ups.

        """

        return self.power_ups