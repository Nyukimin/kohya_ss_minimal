# LoRAタブのTrainingタブ「Start training」ボタン押下時の挙動

## 概要

LoRAタブのTrainingタブで「Start training」ボタンを押した瞬間からの処理フローを説明するドキュメントです。

## 処理フロー

### 1. ボタンクリックイベントのバインド

**ファイル**: `kohya_gui/lora_gui.py` 3081-3086行目

```python
executor.button_run.click(
    train_model,
    inputs=[dummy_headless] + [dummy_db_false] + settings_list,
    outputs=[executor.button_run, executor.button_stop_training, run_state],
    show_progress=False,
)
```

- `executor.button_run` は `CommandExecutor` クラスのインスタンス（2791行目で生成）
- クリック時に `train_model` 関数が呼び出される

### 2. train_model関数の実行開始

**ファイル**: `kohya_gui/lora_gui.py` 742行目から

#### 2.1 最初の処理（986-994行目）

```python
# パラメータのリスト化
parameters = list(locals().items())
global train_state_value

# UI更新用の値
TRAIN_BUTTON_VISIBLE = [
    gr.Button(visible=True),
    gr.Button(visible=False or headless),
    gr.Textbox(value=train_state_value),
]
```

#### 2.2 実行中のチェック（996-998行目）

```python
if executor.is_running():
    log.error("Training is already running. Can't start another training session.")
    return TRAIN_BUTTON_VISIBLE
```

既にトレーニングが実行中の場合は、エラーログを出力して処理を終了します。

#### 2.3 ログ出力（1000行目）

```python
log.info(f"Start training LoRA {LoRA_type} ...")
```

### 3. バリデーション処理

#### 3.1 LRスケジューラーの引数検証（1002-1004行目）

```python
log.info(f"Validating lr scheduler arguments...")
if not validate_args_setting(lr_scheduler_args):
    return TRAIN_BUTTON_VISIBLE
```

#### 3.2 オプティマイザーの引数検証（1006-1008行目）

```python
log.info(f"Validating optimizer arguments...")
if not validate_args_setting(optimizer_args):
    return TRAIN_BUTTON_VISIBLE
```

#### 3.3 Flux1チェックボックスの検証（1010-1020行目）

```python
if flux1_checkbox:
    log.info(f"Validating lora type is Flux1 if flux1 checkbox is checked...")
    if (
        (LoRA_type != "Flux1")
        and (LoRA_type != "Flux1 OFT")
        and ("LyCORIS" not in LoRA_type)
    ):
        log.error(
            "LoRA type must be set to 'Flux1', 'Flux1 OFT' or 'LyCORIS' if Flux1 checkbox is checked."
        )
        return TRAIN_BUTTON_VISIBLE
```

#### 3.4 パスの検証（1026-1062行目）

以下のパスを検証します：

- `dataset_config` ファイルパス
- `log_tracker_config` ファイルパス
- `logging_dir` フォルダパス（書き込み可能、存在しない場合は作成）
- `LyCORIS_preset` TOMLファイル
- `network_weights` ファイルパス
- `output_dir` フォルダパス（書き込み可能、存在しない場合は作成）
- `pretrained_model_name_or_path` モデルパス
- `reg_data_dir` フォルダパス
- `resume` フォルダパス
- `train_data_dir` フォルダパス
- `vae` モデルパス

各検証で失敗した場合、`TRAIN_BUTTON_VISIBLE` を返して処理を終了します。

#### 3.5 その他の検証（1068-1099行目）

- `bucket_reso_steps` が1以上であること
- `noise_offset` が0-1の範囲内であること
- `output_dir` が存在しない場合は作成
- `stop_text_encoder_training` の警告処理
- 既存モデルのチェック

### 4. 設定の計算と準備（1107-1237行目）

#### 4.1 データセット設定ファイルがある場合（1107-1133行目）

- `max_train_steps` の計算
- `stop_text_encoder_training` の計算
- `lr_warmup_steps` の計算

#### 4.2 データセット設定ファイルがない場合（1135-1230行目）

- `train_data_dir` のサブフォルダを走査
- 各フォルダのリピート数と画像数をカウント
- `total_steps` の計算
- `reg_data_dir` の有無による `reg_factor` の設定（1 または 2）
- `max_train_steps` の計算
- `stop_text_encoder_training` の計算
- `lr_warmup_steps` の計算

#### 4.3 ログ出力（1232-1237行目）

```python
log.info(f"Train batch size: {train_batch_size}")
log.info(f"Gradient accumulation steps: {gradient_accumulation_steps}")
log.info(f"Epoch: {epoch}")
log.info(max_train_steps_info)
log.info(f"stop_text_encoder_training = {stop_text_encoder_training}")
log.info(f"lr_warmup_steps = {lr_warmup_steps}")
```

### 5. コマンドの構築（1239-1799行目）

#### 5.1 Accelerateコマンドの準備（1239-1244行目）

```python
accelerate_path = get_executable_path("accelerate")
if accelerate_path == "":
    log.error("accelerate not found")
    return TRAIN_BUTTON_VISIBLE

run_cmd = [rf"{accelerate_path}", "launch"]
```

#### 5.2 AccelerateLaunch.run_cmd()の呼び出し（1246-1260行目）

Accelerate起動パラメータをコマンドに追加します。

#### 5.3 トレーニングスクリプトの選択（1262-1269行目）

```python
if sdxl:
    run_cmd.append(rf"{scriptdir}/sd-scripts/sdxl_train_network.py")
elif flux1_checkbox:
    run_cmd.append(rf"{scriptdir}/sd-scripts/flux_train_network.py")
elif sd3_checkbox:
    run_cmd.append(rf"{scriptdir}/sd-scripts/sd3_train_network.py")
else:
    run_cmd.append(rf"{scriptdir}/sd-scripts/train_network.py")
```

#### 5.4 ネットワークモジュールと引数の設定（1271-1464行目）

LoRAタイプに応じて `network_module` と `network_args` を設定します。

#### 5.5 学習率の設定と検証（1465-1507行目）

- `text_encoder_lr` と `t5xxl_lr` の組み合わせ検証
- 学習率の変換とリスト化
- 有効な学習率のログ出力
- 学習率の検証（すべて0の場合はエラー）

#### 5.6 TOML設定ファイルの構築（1527-1772行目）

`config_toml_data` ディクショナリにすべての設定パラメータを構築します。

#### 5.7 TOML設定ファイルの保存（1779-1791行目）

```python
current_datetime = datetime.now()
formatted_datetime = current_datetime.strftime("%Y%m%d-%H%M%S")
tmpfilename = rf"{output_dir}/config_lora-{formatted_datetime}.toml"

with open(tmpfilename, "w", encoding="utf-8") as toml_file:
    toml.dump(config_toml_data, toml_file)

run_cmd.append("--config_file")
run_cmd.append(rf"{tmpfilename}")
```

#### 5.8 run_cmd_advanced_training()の呼び出し（1793-1799行目）

追加パラメータをコマンドに追加します。

### 6. トレーニングの実行（1801-1831行目）

#### 6.1 print_onlyがFalseの場合（1803-1831行目）

##### 6.1.1 設定ファイルの保存（1804-1816行目）

```python
current_datetime = datetime.now()
formatted_datetime = current_datetime.strftime("%Y%m%d-%H%M%S")
file_path = os.path.join(output_dir, f"{output_name}_{formatted_datetime}.json")

log.info(f"Saving training config to {file_path}...")

SaveConfigFile(
    parameters=parameters,
    file_path=file_path,
    exclusion=["file_path", "save_as", "headless", "print_only"],
)
```

##### 6.1.2 環境設定（1819行目）

```python
env = setup_environment()
```

##### 6.1.3 コマンドの実行（1823行目）⭐ **実際のトレーニングプロセスが起動される**

```python
executor.execute_command(run_cmd=run_cmd, env=env)
```

この時点で `CommandExecutor.execute_command()` メソッドが呼び出されます。

**ファイル**: `kohya_gui/class_command_executor.py` 31-51行目

```python
def execute_command(self, run_cmd: str, **kwargs):
    if self.process and self.process.poll() is None:
        log.info("The command is already running. Please wait for it to finish.")
    else:
        command_to_run = " ".join(run_cmd)
        log.info(f"Executing command: {command_to_run}")
        
        # Execute the command securely
        self.process = subprocess.Popen(run_cmd, **kwargs)
        log.debug("Command executed.")
```

この `subprocess.Popen()` が実際のトレーニングプロセスを起動します。

##### 6.1.4 トレーニング状態の更新（1825行目）

```python
train_state_value = time.time()
```

##### 6.1.5 UI更新（1827-1831行目）

```python
return (
    gr.Button(visible=False or headless),  # Start trainingボタンを非表示
    gr.Button(visible=True),               # Stop trainingボタンを表示
    gr.Textbox(value=train_state_value),   # 状態を更新
)
```

## 処理の流れのまとめ

1. **ボタンクリック** → `train_model` 関数が呼び出される
2. **実行中チェック** → 既に実行中の場合はエラーで終了
3. **バリデーション** → 各種パラメータとパスの検証
4. **設定の計算** → 学習ステップ数、ウォームアップステップ数などの計算
5. **コマンド構築** → Accelerateコマンドとトレーニングスクリプトのコマンドを構築
6. **設定ファイル保存** → TOML設定ファイルとJSON設定ファイルを保存
7. **プロセス起動** → `subprocess.Popen()` でトレーニングプロセスを起動
8. **UI更新** → ボタンの表示/非表示を切り替え

## 重要なポイント

- **実際のトレーニングプロセスが起動されるのは** `CommandExecutor.execute_command()` メソッド内の `subprocess.Popen()` です（`class_command_executor.py` 50行目）
- この時点で、`run_cmd` は `accelerate launch` コマンドとトレーニングスクリプト（`train_network.py` など）のリストになっています
- `subprocess.Popen()` は非ブロッキングで実行されるため、すぐに次の処理（UI更新）に進みます
- トレーニングプロセスはバックグラウンドで実行され続けます

## コード上の位置

- **ボタンのイベントハンドラー**: `kohya_gui/lora_gui.py` 3081-3086行目
- **train_model関数**: `kohya_gui/lora_gui.py` 742-1831行目
- **CommandExecutor.execute_command()**: `kohya_gui/class_command_executor.py` 31-51行目
- **実際のプロセス起動**: `kohya_gui/class_command_executor.py` 50行目（`subprocess.Popen()`）

## Minimalタブとの統合

### Minimalタブからの引数反映

Minimalタブ（`minimal/sdxl_simple_tab.py`）で設定したパラメータは、以下の流れでコマンド実行に反映されます：

1. **Minimalタブの「Start training」ボタンクリック**（316-321行目）
   ```python
   self.train_button.click(
       fn=self.start_training,
       inputs=self._get_all_inputs(),
       outputs=[self.output_log],
       show_progress=True
   )
   ```

2. **start_training()メソッドの実行**（362-427行目）
   - UIの入力値を検証
   - `_convert_ui_to_train_args()` で引数変換
   - 既存の `train_model()` 関数を呼び出し

3. **_convert_ui_to_train_args()による引数変換**（505-688行目）
   - UIの16個の入力値を `train_model()` 関数の引数形式（243個）に変換
   - プリセット値（`SDXL_FACE_LORA_DEFAULTS`）と固定値（`SDXL_FACE_LORA_FIXED`）をマージ
   - UIからの値で上書き

4. **train_model()関数の実行**
   - Minimalタブから変換された引数が `train_model(*args)` として渡される
   - 以降の処理は通常のTrainingタブと同じフロー

5. **コマンド実行（1823行目）**
   ```python
   executor.execute_command(run_cmd=run_cmd, env=env)
   ```
   - Minimalタブで設定したパラメータは、この時点で `run_cmd` に含まれている

### 重要な注意点

**⚠️ 現在の実装上の問題**

`_convert_ui_to_train_args()` メソッドが返す引数リスト（688行目で終了）が、`train_model()` 関数が期待する243個の引数に満たない可能性があります。

特に以下の引数が不足している可能性があります：
- `text_encoder_lr` (868行目) - UIから取得しているが、引数リストに含まれていない可能性
- `network_dim` (871行目) - UIから取得しているが、引数リストに含まれていない可能性  
- `network_alpha` (874行目) - UIから取得しているが、引数リストに含まれていない可能性
- その他、位置115以降の引数（約116個）

**確認方法**

Minimalタブで学習を開始した際に、実際にコマンドに反映されているか確認するには：

1. `train_model()` 関数内の `run_cmd` 構築部分（1239-1799行目）で、Minimalタブで設定した値が正しく使用されているか確認
2. 特に `text_encoder_lr`、`network_dim`、`network_alpha` がTOML設定ファイル（1527-1772行目）に正しく含まれているか確認
3. 最終的に生成される `run_cmd` に、これらのパラメータが含まれているか確認

**結論**

理論的には、Minimalタブの引数は `_convert_ui_to_train_args()` で変換されて `train_model()` に渡され、最終的に `executor.execute_command(run_cmd=run_cmd, env=env)` の `run_cmd` に反映されるはずです。しかし、`_convert_ui_to_train_args()` の実装が不完全な場合、一部の引数が正しく反映されない可能性があります。
