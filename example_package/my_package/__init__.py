

print('__init__.py is runing')
# -------------------------------------------------------- #
#! import my_module
# これはエラー．pythonは，my_moduleの場所がわからない
# -------------------------------------------------------- #
#! from . import my_module
# my_package.my_moduleとして使えるようになる．
# -------------------------------------------------------- #
#! from . import *
# 何もインポートされない
# -------------------------------------------------------- #
#! import my_package.my_module
#　my_package.my_module
#　my_package.my_package
# がつかえるようになる
# -------------------------------------------------------- #
#! from my_package import *
# これは，ファイルmy_package.pyの中に記述してあるクラスや関数を読み込むだけ
# ここには何も定義されていない．my_module.pyはインポートされない
# -------------------------------------------------------- #
#! from .my_module import *
# my_package.my_class(  my_package.my_func(   my_package.my_module
# として使えるようになる
# -------------------------------------------------------- #
#! from .my_module import *
# my_package.my_class(  my_package.my_func(   my_package.my_module
# として使えるようになる
# これを使えば，
# from my_package import my_classなどができ，これは標準のmathパッケージと同じように使えている
# ただ何がインポートされているかわかりにくいという欠点がある．．
# -------------------------------------------------------- #
from .my_module import my_class
from .my_module import my_func
# 長くなるが，これだと何をインポートしているかわかる．