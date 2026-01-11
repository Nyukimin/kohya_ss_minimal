# kohya-ss 起動プロセスフロー

## 概要

kohya-ss本体の起動プロセスを説明するドキュメントです。

## 最後に起動されるプロセス

**最後に起動されるプロセスは `Gradio の Blocks.launch()` メソッドです。**

このメソッドが内部でWebサーバー（FastAPIベース）を起動し、指定されたポート（デフォルト: 7860）でリスニングを開始します。

## 実行フロー詳細

### 1. エントリーポイント

**ファイル**: `kohya_gui.py`

```python
if __name__ == "__main__":
    # 引数パーサーの初期化と引数の解析
    parser = initialize_arg_parser()
    args = parser.parse_args()
    
    # ログ設定
    log = setup_logging(debug=args.debug)
    
    # 要件検証（--noverifyが指定されていない場合）
    if not args.noverify:
        subprocess.run(validation_command, check=True)
    
    # UI関数を呼び出し
    UI(**vars(args))
```

### 2. UI関数の実行

**ファイル**: `kohya_gui.py` の `UI()` 関数（74-111行目）

実行順序：

1. **JavaScriptの追加** (76行目)
   ```python
   add_javascript(kwargs.get("language"))
   ```

2. **リリース情報とREADMEの読み込み** (80-81行目)
   ```python
   release_info = read_file_content("./.release")
   readme_content = read_file_content("./README.md")
   ```

3. **設定ファイルの読み込み** (84行目)
   ```python
   config = KohyaSSGUIConfig(config_file_path=kwargs.get("config"))
   ```

4. **Gradio UIインターフェースの初期化** (94行目)
   ```python
   ui_interface = initialize_ui_interface(config, ...)
   ```

5. **Gradioサーバーの起動** (111行目) ⭐ **最後に実行されるプロセス**
   ```python
   ui_interface.launch(**launch_params)
   ```

### 3. Gradio Blocks.launch() の動作

`ui_interface.launch()` メソッドが実行されると：

- Gradioライブラリが内部でWebサーバー（FastAPI/Uvicorn）を起動
- 指定されたIPアドレス（デフォルト: 127.0.0.1）とポート（デフォルト: 7860）でリスニング
- ブラウザで自動的に開く（`--inbrowser`が指定されている場合）
- Webインターフェースが利用可能になる

## 起動パラメータ

`launch()` メソッドに渡されるパラメータ（`kohya_gui.py` 97-108行目）：

- `server_name`: リスンするIPアドレス（デフォルト: 127.0.0.1）
- `server_port`: ポート番号（デフォルト: 0 = 自動割り当て、通常は7860）
- `auth`: ユーザー名とパスワード（認証が有効な場合）
- `inbrowser`: ブラウザを自動で開くかどうか
- `share`: Gradioの共有リンクを作成するかどうか
- `root_path`: リバースプロキシ用のルートパス
- `debug`: デバッグモード

## コード上の位置

- **エントリーポイント**: `kohya_gui.py` 135-156行目
- **UI関数**: `kohya_gui.py` 74-111行目
- **最後のプロセス起動**: `kohya_gui.py` 111行目
  ```python
  ui_interface.launch(**launch_params)
  ```

## 補足：subprocessで実行される処理

`UI()` 関数が呼ばれる前に、以下のsubprocessが実行される場合があります：

1. **要件検証プロセス** (`kohya_gui.py` 148-153行目)
   ```python
   validation_command = [PYTHON, os.path.join(project_dir, "setup", "validate_requirements.py")]
   subprocess.run(validation_command, check=True)
   ```

   これは `--noverify` が指定されていない場合のみ実行されます。

## まとめ

kohya-ss本体の起動において、**最後に起動されるプロセスは Gradio の Webサーバー（`ui_interface.launch()`）** です。

このメソッドが実行されると、Gradioフレームワークが内部でHTTPサーバーを立ち上げ、Webインターフェースを提供します。このプロセスは、ユーザーがGUIにアクセスできるようになるまで、プロセスとして継続的に実行されます。
