# 🏰 Castle Defense

A feature‑rich, extendable **tower‑defense** game written in **Python** with **Pygame**.  
Defend your castle from relentless waves of monsters by building, upgrading, and strategically placing towers.  
Advance your settlement with a village system, research powerful upgrades, and master tiered monster challenges.

---

## 📑 Table of Contents
1. [Gameplay Features](#-gameplay-features)
2. [Architecture Overview](#-architecture-overview)
3. [Project Structure](#-project-structure)
4. [Getting Started](#-getting-started)
5. [Controls & Tips](#-controls--tips)
6. [Roadmap](#-roadmap)
7. [Contributing](#-contributing)
8. [License](#-license)

---

## 🎮 Gameplay Features

- **Tower Defense Core Loop** – Procedurally generated enemy waves challenge your defenses.
- **Castle System** – A central, upgradeable stronghold; losing it means game over.
- **Village Mode** – Unlock new buildings (Storage Barn, Coresmith, Monster Codex, etc.) that grant bonuses and research.
- **Towers & Upgrades** – Multiple tower archetypes with item‑slot upgrading and ability modifiers.
- **Challenge Tiers** – Bronze, Silver, Gold, and Platinum monster challenges unlock rare loot.
- **Resource Management** – Gather, store, and spend resources through the `ResourceManager`.
- **Rich UI** – Container‑based UI, tower & building menus, notifications, and a dev menu (press **Ctrl + D**).
- **Save/Load** – Persistent saves handled by `SaveManager`.
- **Extensibility** – Clean registry & factory patterns make adding new content straightforward.

---

## 🛠️ Architecture Overview

| Layer | Key Modules | Responsibilities |
|-------|-------------|------------------|
| **Core Loop** | `main.py`, `game.py` | Game loop, state updates, rendering, event dispatch. |
| **State Management** | `GameStateManager`, individual state classes | Main menu, playing, paused, build mode, etc. |
| **Entities & Components** | `registry.py`, factories, feature packages | Towers, enemies, buildings, projectiles. |
| **Systems** | `ResourceManager`, `AnimationManager`, `SaveManager` | Resources, animations, persistence, challenges. |
| **Config** | `config.py`, `config_extension.py` | Tunable constants and live config overrides. |
| **UI** | `ui/` package | Reusable widgets, layouts, in‑game HUD. |

---

## 📂 Project Structure

```text
Castle-Defense/
├── main.py                  # Entry‑point & main loop
├── game.py                  # Core Game class
├── config.py                # Static configuration
├── config_extension.py      # Hot‑reloadable overrides
├── loot_tables.py           # Loot & drop mechanics
├── registry.py              # Component registry
├── resource_icons.py        # SVG icon handling
├── save_system.py           # Save/load logic
├── utils.py                 # Helper functions
├── features/                # Towers, castle, village, challenges…
├── ui/                      # Modular UI components
└── assets/                  # Art, SFX, music, fonts
```

---

## ▶️ Getting Started

1. **Prerequisites**

   ```bash
   python -m pip install --upgrade pip
   pip install pygame
   ```

2. **Run the Game**

   ```bash
   python main.py
   ```

3. **Optional Dev Tools**

   - Press **Ctrl + D** in‑game to open the Developer Menu (toggle debug draw, adjust speed, spawn enemies).

---

## 🎮 Controls & Tips

| Action | Default Key / Mouse | Notes |
|--------|--------------------|-------|
| Select tower/building | Left‑click | Hotbar at bottom. |
| Place tower | Left‑click on valid tile | Range overlay shows coverage. |
| Cancel placement | Right‑click or **Esc** | |
| Upgrade tower | Select placed tower then click **Upgrade** | Consumes resources. |
| Toggle dev menu | **Ctrl + D** | Developer utilities. |
| Pause | **P** or **Esc** | |

*Pro tip:* Upgrade storage early to avoid resource overflow, and leverage research to unlock powerful tier‑2 towers.

---

## 🚧 Roadmap

- 🔄 **Co‑op / Multiplayer**
- 🧠 Enhanced enemy pathfinding
- 🌲 Biome‑based maps & environmental hazards
- 🔉 Audio system overhaul
- 🎨 Custom UI themes/skins
- 📜 Steam & itch.io release

---

## 🤝 Contributing

Pull requests are welcome! Please open an issue first to discuss major changes.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingThing`)
3. Commit your changes (`git commit -am 'Add amazing thing'`)
4. Push to the branch (`git push origin feature/AmazingThing`)
5. Open a Pull Request

---

## 📜 License

Distributed under the **MIT License**.  
See [`LICENSE`](LICENSE) for more information.
