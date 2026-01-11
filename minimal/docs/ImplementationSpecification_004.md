# SDXL Face LoRA Minimal Tab Implementation Specification (004)
**Version:** 4.0  
**Date:** 2026-01-11  
**Status:** 現状実装反映 + ギャップ整理（次実装: Caption/Repeat）

## 概要

本ドキュメントは、`kohya_ss_minimal/minimal` の **現状実装（2026-01-11時点）を事実ベースで反映**し、
`Specification_001.md` の要求に対して **満たせている点/不足している点（ギャップ）**を明確化する。

## 現状の実装状況（実コード準拠）

### 統合方法
- `kohya_gui/lora_gui.py` に Minimal タブを追加し、`minimal/sdxl_simple_tab.py` を読み込む
- 学習実行は **既存 `kohya_gui.lora_gui.train_model()` を呼ぶ**（学習コアは変更しない）

### Minimal UI（`minimal/sdxl_simple_tab.py`）に存在するセクション
- Model Source
- Training Data
- Training Parameters
- Output
- Training

### config.toml 保存（自動保存 + 明示保存）
- **UI値変更時**: `auto_save_config()` 経由で `config.toml` に保存
  - UI表示は `✓ Auto-saved`
- **Save Config ボタン**: 明示保存として保存し、成功メッセージを返す
  - `設定をconfig.tomlに保存しました`

> 注: 2026-01-11時点で Save Config は「明示保存フラグ」を渡す実装に更新済み。

### テスト
- `minimal/tests` の pytest は **23 tests 全て合格**

## 仕様（Specification_001.md）とのギャップ

### 1) Caption一括生成（必須）
- **仕様要求**: 固定 caption を全画像へ一括生成、既存 `.txt` は上書き確認
- **現状**: Minimal UI に Caption セクション/生成ボタンが無い
- **既存流用候補**:
  - `kohya_gui/basic_caption_gui.caption_images()`（内部で `tools/caption.py` を呼ぶ）

#### 推奨実装方針（最小変更）
- Minimal に `Caption` Accordion を追加
- UI項目（例）
  - caption_text（Textbox）
  - caption_extension（Textbox/Dropdown, default `.txt`）
  - overwrite（Checkbox）
  - generate（Button）
- 上書き確認
  - Gradio はネイティブのモーダル確認が弱いので、
    - 既存 `.txt` 件数を事前に数える
    - overwrite がOFFなら「既存captionがN件ある」旨をログ表示して停止
    - overwrite がONなら実行
  - さらに厳密に行う場合は `Confirm/Cancel` ボタンを表示切替するパターン（gr.State + update）を採用

### 2) Repeat（num_repeats）/ dataset_config.toml
- **仕様要求**: repeat を数値でUI指定し、`dataset_config.toml` を生成して使用
- **現状**:
  - Minimal UI に `num_repeats` 入力が無い
  - `dataset_config` は `presets.py` で空文字のまま
  - `train_data_dir` を直接 `train_model()` に渡している

#### 推奨実装方針
- Minimal に `num_repeats` を追加
- `dataset_config.toml` を最小構成で生成し、`train_model()` の `dataset_config` 引数へ渡す

## 技術スタック整合
- リポジトリの `pyproject.toml` は `requires-python = ">=3.10,<3.12"`
- 実装仕様書内で Python 3.12+ と書かれている箇所がある場合は誤りとして扱い、今後は本設定に合わせる

## 更新履歴
- v4.0 (2026-01-11)
  - 現状実装の反映（Save Config の明示保存挙動を含む）
  - Caption一括生成、Repeat/dataset_config の不足をギャップとして明文化
