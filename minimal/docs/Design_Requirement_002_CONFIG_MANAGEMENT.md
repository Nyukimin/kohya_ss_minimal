# 設計要件: Minimalタブの設定管理

## 要件定義

**Minimalタブの設定は、DEFAULT（システムデフォルト）をベースに、CONFIG（ユーザー設定）で上書きする。**

## 設計原則

### 一貫したシーケンス

CONFIGの有無に関わらず、常に同じ処理フローを通ることで、バグを減らす。

```
1. DEFAULTで初期化
2. CONFIGで上書き
3. 結果を使用
```

### 処理フロー

```
サーバ起動時:
    1. MINIMAL_DEFAULT_CONFIG を読み込む（presets.py）
    2. 初期UI描画用に使用

Minimalタブ描画時（Tab.select()）:
    1. MINIMAL_DEFAULT_CONFIG をコピー
    2. config.toml を読み込み（load_user_config()）
    3. CONFIGで上書き（config.update(user_config)）
    4. gr.update() で各UIコンポーネントを更新

タブ内の値変更時:
    1. 変更された値を config.toml に保存（save_config()）
```

## 実装詳細

### 1. load_and_update_ui() メソッド

タブ選択時に呼び出され、最新のCONFIGでUIを更新する。

```python
def load_and_update_ui(self):
    """タブ選択時にDEFAULT→CONFIGの順で読み込み、UIを更新"""
    # 1. DEFAULTで初期化
    config = MINIMAL_DEFAULT_CONFIG.copy()
    
    # 2. CONFIGで上書き
    user_config = load_user_config()
    config.update(user_config)
    
    # 3. gr.update()でUIを更新
    return (
        gr.update(value=config.get('pretrained_model_name_or_path', '')),
        gr.update(value=config.get('train_data_dir', '')),
        gr.update(value=config.get('output_name', '')),
        gr.update(value=config.get('output_dir', '')),
        # ... 全コンポーネント
    )
```

### 2. Tab.select() イベントバインド

```python
# lora_gui.py で Tab.select() をバインド
with gr.Tab("Minimal") as minimal_tab:
    tab_instance = sdxl_simple_tab(headless=headless, config=config, use_shell_flag=use_shell)
    minimal_tab.select(
        fn=tab_instance.load_and_update_ui,
        outputs=tab_instance.get_ui_outputs()
    )
```

### 3. 自動保存の廃止

**重要**: 自動保存（.change()イベント）は廃止された。

理由: Gradioでは .change() イベントが Tab.select() より先に発火するため、
config.toml が意図せず空の値で上書きされる問題があった。

代わりに「Save Config」ボタンによる明示保存のみをサポート。

## 利点

| 観点 | 効果 |
|------|------|
| 一貫性 | CONFIGの有無に関わらず同じシーケンス |
| 予測可能性 | 常に同じコードパスを通る |
| デバッグ容易性 | 問題の原因特定が容易 |
| 拡張性 | 新パラメータ追加時も同じパターン |
| 安全性 | KeyErrorが発生しない |

## ファイル変更

1. **minimal/sdxl_simple_tab.py**
   - `load_and_update_ui()` メソッド追加
   - `get_ui_outputs()` メソッド追加
   - `auto_save_config()` 簡素化
   - UI初期値を `MINIMAL_DEFAULT_CONFIG` から取得（`MINIMAL_USER_CONFIG` 参照を削除）

2. **kohya_gui/lora_gui.py**
   - `gr.Tab("Minimal") as minimal_tab` でタブ参照を取得
   - `minimal_tab.select()` イベントをバインド

## 関連ドキュメント

- **Design_Requirement_001.md**: Start Training ボタンの設計要件
- **ImplementationSpecification_FULL.md**: 実装仕様全体
