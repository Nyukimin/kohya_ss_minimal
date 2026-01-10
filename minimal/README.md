# Minimal - SDXL Face LoRA Simple Interface

This directory contains the minimal SDXL face LoRA training interface for kohya_ss. It provides a simplified UI that reduces complexity and prevents common mistakes when training SDXL face LoRAs.

## Directory Structure

```
minimal/
├── README.md                            # This file
├── __init__.py                          # Python package init
├── sdxl_simple_tab.py                   # UI implementation (calls existing functions)
├── presets.py                           # SDXL face LoRA default values
├── config.toml                          # Reference configuration
├── docker-compose.yaml                  # Minimal Docker setup
└── docs/                               # Implementation documentation
    ├── Specification_001.md            # Project specification
    └── ImplementationSpecification_002.md  # Implementation details (v2.0)
```

## Design Philosophy

**Minimal is UI-only layer that uses existing kohya-ss functionality.**

- **UI Layer Only**: Provides parameter input interface only
- **Uses Existing Logic**: Calls existing train_model() function from lora_gui.py
- **No Duplicate Processing**: Caption generation, dataset setup, training execution use existing functions
- **Minimal Changes**: Only adds one subtab to the main codebase

## Integration

The minimal interface integrates into the main kohya-ss GUI as a "Minimal" tab at the same level as Training, Tools, and Guides within the LoRA tab:

**LoRA** → **Training** | **Tools** | **Minimal** | **Guides**

## Features

- **Simplified SDXL Interface**: Essential parameters only for face LoRA training
- **Optimized Defaults**: Pre-configured values based on SDXL face LoRA best practices
- **Accordion Layout**: Organized sections matching kohya-ss design patterns
- **Error Prevention**: Reduced parameter options to prevent common mistakes
- **Existing Integration**: Uses all existing kohya-ss caption, dataset, and training functions

## Core Files

### Implementation
- **sdxl_simple_tab.py**: Main UI class that calls existing train_model() function
- **presets.py**: SDXL face LoRA optimized default values and choices

### Configuration
- **config.toml**: Reference configuration with optimal SDXL face LoRA settings
- **docker-compose.yaml**: Minimal Docker setup for SDXL training only

### Documentation
- **docs/Specification_001.md**: Project background and requirements
- **docs/ImplementationSpecification_002.md**: Corrected technical implementation

## Installation

The minimal interface is automatically available when the `minimal/` directory exists in the kohya_ss project root. No additional installation required.

**To Remove**: Simply delete the `minimal/` directory and remove 8 lines from `kohya_gui/lora_gui.py`

## Usage

1. Start kohya_ss GUI
2. Navigate to **LoRA** tab  
3. Click **Minimal** subtab
4. Configure SDXL face LoRA training with simplified interface
5. Training uses existing kohya-ss processing pipeline

## Dependencies

- gradio (UI framework)
- All standard kohya-ss dependencies
- No additional packages required

---

# Minimal - SDXL顔LoRA簡易インターフェース

このディレクトリには、kohya_ss用のSDXL顔LoRA学習簡易インターフェースが含まれています。SDXL顔LoRA学習時の複雑さを軽減し、よくある間違いを防ぐ簡潔なUIを提供します。

## ディレクトリ構成

```
minimal/
├── README.md                            # このファイル
├── __init__.py                          # Pythonパッケージ初期化
├── sdxl_simple_tab.py                   # UI実装（既存関数呼び出し）
├── presets.py                           # SDXL顔LoRAデフォルト値
├── config.toml                          # 参考設定
├── docker-compose.yaml                  # 最小限Docker設定
└── docs/                               # 実装ドキュメント
    ├── Specification_001.md            # プロジェクト仕様
    └── ImplementationSpecification_002.md  # 実装詳細（v2.0）
```

## 設計思想

**MinimalはUI専用レイヤーで、既存のkohya-ss機能をそのまま利用します。**

- **UIレイヤーのみ**: パラメータ入力インターフェースのみを提供
- **既存ロジック活用**: lora_gui.pyの既存train_model()関数を呼び出し
- **処理重複なし**: caption生成、dataset設定、学習実行は既存関数を使用
- **最小修正**: メインコードベースにはサブタブ1つの追加のみ

## 統合方法

minimal インターフェースは、メインkohya-ss GUIのLoRAタブ内で、Training、Tools、Guidesと同じ階層の「Minimal」タブとして統合されます:

**LoRA** → **Training** | **Tools** | **Minimal** | **Guides**

## 機能

- **簡潔なSDXLインターフェース**: 顔LoRA学習用の必要最小限パラメータのみ
- **最適化済みデフォルト**: SDXL顔LoRAベストプラクティスに基づく事前設定値
- **Accordionレイアウト**: kohya-ssデザインパターンに合わせた整理されたセクション
- **エラー防止**: パラメータ選択肢を減らしてよくある間違いを防止
- **既存統合**: 既存のkohya-ss caption、dataset、学習関数をすべて使用

## コアファイル

### 実装
- **sdxl_simple_tab.py**: 既存のtrain_model()関数を呼び出すメインUIクラス
- **presets.py**: SDXL顔LoRA最適化済みデフォルト値と選択肢

### 設定
- **config.toml**: 最適なSDXL顔LoRA設定での参考設定
- **docker-compose.yaml**: SDXL学習専用の最小限Docker設定

### ドキュメント
- **docs/Specification_001.md**: プロジェクト背景と要求事項
- **docs/ImplementationSpecification_002.md**: 修正版技術実装詳細

## インストール

minimal インターフェースは、kohya_ssプロジェクトルートに`minimal/`ディレクトリが存在すると自動的に利用可能になります。追加インストールは不要です。

**削除方法**: `minimal/`ディレクトリを削除し、`kohya_gui/lora_gui.py`から8行を削除するだけ

## 使用方法

1. kohya_ss GUIを起動
2. **LoRA**タブに移動
3. **Minimal**サブタブをクリック
4. 簡潔なインターフェースでSDXL顔LoRA学習を設定
5. 学習は既存のkohya-ss処理パイプラインを使用

## 依存関係

- gradio (UIフレームワーク)
- 標準kohya-ss依存関係すべて
- 追加パッケージは不要

---

**Project**: kohya_ss_minimal  
**Version**: 2.0  
**Last Updated**: 2026-01-10