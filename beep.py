import pdb
import traceback


def assert_(xyz):
    tb = traceback.extract_stack()
    # pop last stack frame so that new last frame is inside validation test
    tb.pop()
    if not xyz:
        raise BeepException


class BeepException(BaseException):
    def __init__(self) -> None:
        super().__init__("woops")


def main():
    try:
        a = 1
        b = 2
        # assert_(True)
        assert_(False)
        # assert_(1 / 0)
        a + b
    except BeepException as exc:
        tb = exc.__traceback__
        breakpoint()

        # tb.tb_next = None

        # tbi = tb
        # if tbi.tb_next.tb_next:
        #   while tbi.tb_next.tb_next:
        #       tbi = tbi.tb_next
        #   tbi.tb_next = None  # Remove the frame inside the assert_ rewritten function

        tbi = tb
        while tbi.tb_next:
            if tbi.tb_next.tb_frame.f_code.co_name == 'assert_':
                tbi.tb_next = None
                break
            tbi = tbi.tb_next

        pdb.post_mortem(tb)
    except Exception as exc:
        print('Exception')
        tb = exc.__traceback__
        pdb.post_mortem(tb)


if __name__ == '__main__':
    main()
