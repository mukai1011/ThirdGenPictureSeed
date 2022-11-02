from Commands.PythonCommandBase import ImageProcPythonCommand
from Commands.Keys import Hat

from .gc_button_alias import Button
from .picture_seed_util import WaitThread, execute
from .pokecon_extension import execute_sequence, repeat

DEFAULT_DURATION = 0.1

class Reset():
    """リセットして、マルチブート待機までの操作を定義するクラス
    """
    def __init__(self, command: ImageProcPythonCommand):
        self.__command = command
    def run(self):
        execute_sequence(self.__command, [
            # Zメニューを開く
            (Button.Z, DEFAULT_DURATION, 2),
            # カートリッジこうかん
            (Button.A, DEFAULT_DURATION, 1),
            # 「ゲームを終了してカートリッジを交換しますか？」「いいえ」
            (Hat.LEFT, DEFAULT_DURATION, 1),
            # 「はい」
            (Button.A, DEFAULT_DURATION, 1),
            # 「カートリッジを交換してください。」
            (Button.A, DEFAULT_DURATION, 1),
            ([Button.START, Button.X], 4, 2),
        ])

class LoadGame():
    """マルチブート待ち受けを解除して、絵画鑑賞の直前までの操作を定義するクラス
    """
    def __init__(self, command: ImageProcPythonCommand):
        self.__command = command
    def run(self):
        execute_sequence(self.__command, [
            # 待ち受け解除
            (Button.A, DEFAULT_DURATION, 6),
            # オープニングをスキップ
            (Button.A, DEFAULT_DURATION, 1.5),
            # タイトル表示までスキップ
            (Button.A, DEFAULT_DURATION, 1.5),
            # 「PUSH START BUTTON」
            (Button.A, DEFAULT_DURATION, 3),
            # 「でんちぎれの　ために　とけいが　うごかなくなりました」
            (Button.A, DEFAULT_DURATION, 2),
            # 「とけいに　かんけいする　できごとは　おきませんが　ゲームを　つづけて　あそぶことは　できます」
            (Button.A, DEFAULT_DURATION, 2),
            # セーブデータ選択
            (Button.A, DEFAULT_DURATION, 2),
        ])

class SeePicture():
    """絵画を見て、離脱する操作を定義するクラス
    """
    def __init__(self, command: ImageProcPythonCommand):
        self.__command = command
    def run(self):
        execute_sequence(self.__command, [
            # 絵画を見る
            (Button.A, DEFAULT_DURATION, 2),
            # 絵画画面から離脱する
            (Button.A, DEFAULT_DURATION, 2),
        ])

class MoveToDestination():
    """絵画を見た直後から、エンカウントの直前まで移動する操作を定義するクラス
    """
    def __init__(self, command: ImageProcPythonCommand):
        self.__command = command
    def run(self):
        execute_sequence(self.__command, [

            # コンテスト会場脱出
            *repeat((Hat.BTM, DEFAULT_DURATION, 0.5), 3),
            *repeat((Hat.LEFT, DEFAULT_DURATION, 0.5), 10),
            *repeat((Hat.BTM, DEFAULT_DURATION, 0.5), 8),
            (Hat.BTM, DEFAULT_DURATION, 3.5),

            # 船着き場まで
            *repeat((Hat.LEFT, DEFAULT_DURATION, 0.5), 16),
            *repeat((Hat.BTM, DEFAULT_DURATION, 0.5), 9),
            *repeat((Hat.RIGHT, DEFAULT_DURATION, 0.5), 5),      
            (Hat.TOP, DEFAULT_DURATION, 0.5),
            (Hat.TOP, DEFAULT_DURATION, 2.5),

            # 移動->会話->乗船
            *repeat((Hat.LEFT, DEFAULT_DURATION, 0.5), 4),
            *repeat((Hat.TOP, DEFAULT_DURATION, 0.5), 4),
            (Button.A, DEFAULT_DURATION, 1.5),
            (Button.A, DEFAULT_DURATION, 1.5),
            (Button.A, DEFAULT_DURATION, 4.5),
            *repeat((Button.A, DEFAULT_DURATION, 0.5), 4),
            (Button.A, DEFAULT_DURATION, 8.5),
            
            # みなみのことう移動
            *repeat((Hat.RIGHT, DEFAULT_DURATION, 0.5), 3),
            *repeat((Hat.TOP, DEFAULT_DURATION, 0.5), 7),
            *repeat((Hat.RIGHT, DEFAULT_DURATION, 0.5), 10),
            *repeat((Hat.TOP, DEFAULT_DURATION, 0.5), 9),
            *repeat((Hat.LEFT, DEFAULT_DURATION, 0.5), 6),
            *repeat((Hat.BTM, DEFAULT_DURATION, 0.5), 2),
            *repeat((Hat.LEFT, DEFAULT_DURATION, 0.5), 6),
            *repeat((Hat.TOP, DEFAULT_DURATION, 0.5), 4),
            (Hat.TOP, DEFAULT_DURATION, 2.5),
            *repeat((Hat.TOP, DEFAULT_DURATION, 0.5), 6),
        ])

class Encounter():
    """エンカウント直前から、エンカウントする操作を定義するクラス
    """
    def __init__(self, command: ImageProcPythonCommand):
        self.__command = command
    def run(self):
        execute_sequence(self.__command, [
            (Button.A, DEFAULT_DURATION, 15),
            (Button.B, DEFAULT_DURATION, 5),
        ])

class PaintSeed(ImageProcPythonCommand):
    
    NAME = '絵画seed乱数調整のテンプレート'

    def __init__(self, cam, gui=None):
        super().__init__(cam, gui)

    def do(self):
        """
        事前条件:
        - Zメニューのカーソルが「カートリッジこうかん」に合っている。
        - ミナモシティのコンテスト会場の左端の絵画の前でセーブしている。
        
        個体情報:
        
        ```plaintext
        フレームカウンタ: 0x661B(F) = 26139 = 7分15秒程度
        待機: 65029(F) = 18分3秒程度
        ひかえめ　めざ炎70

        絵画seedずれ: 63F
        エンカウントずれ: -511F
        ```
        """

        frame_until_seeing = 26139
        calibration_see_picture = 63

        frame_until_encountering = 65029
        calibration_encounter = -511

        operations = (
            Reset(self), 
            LoadGame(self), 
            SeePicture(self), 
            MoveToDestination(self), 
            Encounter(self)
        )
        wait_threads = (
            WaitThread(self, frame_until_seeing, calibration_see_picture), 
            WaitThread(self, frame_until_encountering, calibration_encounter)
        )

        try:
            execute(operations, wait_threads)

        except Exception as e:
            print(f"[ERROR]: 失敗しました。{e.with_traceback(None)}")
