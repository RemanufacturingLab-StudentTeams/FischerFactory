from backend import mqttClient
from ui.screens import homeScreen
from common import logger

if __name__ == "__main__":
    print("Program start!")

logger.setup()
homeScreen.runUI()