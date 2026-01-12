"""
Minimalタブ用のユーティリティ関数

Trainingタブのsettings_list構築ロジックを関数化したもの
"""
import inspect
import logging
from typing import Dict, Any

log = logging.getLogger(__name__)


def build_settings_list_from_params(params: Dict[str, Any]) -> list:
    """
    train_model関数の引数順序（headlessとprint_onlyを除く）と同じ順序でsettings_listを構築
    
    元のロジック（lora_gui.py 2800-3032行目）:
    settings_list = [
        source_model.pretrained_model_name_or_path,  # Gradioコンポーネント
        source_model.v2,  # Gradioコンポーネント
        ...
    ]
    
    この関数は、Gradioコンポーネントではなく、パラメータ辞書から実際の値を取得してリストを構築する
    
    最重要: この関数の順序は、train_model関数の引数順序（headlessとprint_onlyを除く）と
    完全に一致している必要がある。順序が1つでも異なると、間違った引数がtrain_model関数に
    渡され、システム的な崩壊につながる。
    
    Args:
        params: パラメータ辞書（229個のパラメータを含む）
        
    Returns:
        list: train_model関数に渡すsettings_list（229個の実際の値、train_model関数の引数順序と一致）
    """
    # train_model関数の引数順序を取得（headlessとprint_onlyを除く）
    from kohya_gui.lora_gui import train_model
    
    sig = inspect.signature(train_model)
    param_names = list(sig.parameters.keys())[2:]  # headlessとprint_onlyを除く（最初の2つ）
    
    # パラメータ名の順序に従って値を取得
    settings_list = []
    for param_name in param_names:
        value = params.get(param_name)
        # デフォルト値の処理（Noneの場合は空文字列やFalseなど適切なデフォルト値を設定）
        if value is None:
            # パラメータの型に応じてデフォルト値を設定
            param = sig.parameters[param_name]
            if param.default != inspect.Parameter.empty:
                value = param.default
            else:
                # デフォルト値がない場合は、型に応じて推測
                if 'dir' in param_name or 'path' in param_name or 'name' in param_name:
                    value = ''
                elif 'checkbox' in param_name or param_name.startswith('enable_') or param_name.startswith('use_'):
                    value = False
                elif 'lr' in param_name or 'rate' in param_name or 'weight' in param_name:
                    value = 0.0
                elif 'steps' in param_name or 'epoch' in param_name or 'dim' in param_name or 'alpha' in param_name:
                    value = 0
                else:
                    value = ''
        
        settings_list.append(value)
    
    log.info(f"Built settings_list with {len(settings_list)} parameters")
    return settings_list
