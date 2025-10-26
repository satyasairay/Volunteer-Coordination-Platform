#!/usr/bin/env python3
"""Initialize block settings with neon glassmorphic colors"""

from sqlmodel import Session, select
from db import engine, init_db
from models import BlockSettings

# 7 Blocks of Bhadrak with Professional Neon Colors
BLOCK_DEFAULTS = [
    {"block_name": "Bhadrak", "color": "#00FFFF", "glow_intensity": 90},           # Neon Cyan
    {"block_name": "Basudevpur", "color": "#FF00FF", "glow_intensity": 85},        # Neon Magenta
    {"block_name": "Bhandaripokhari", "color": "#00FF00", "glow_intensity": 80},   # Neon Lime
    {"block_name": "Bonth", "color": "#FF6B9D", "glow_intensity": 75},             # Neon Coral
    {"block_name": "Chandabali", "color": "#FFD700", "glow_intensity": 88},        # Neon Gold
    {"block_name": "Dhamnagar", "color": "#9D00FF", "glow_intensity": 85},         # Neon Violet
    {"block_name": "Tihidi", "color": "#FF3D00", "glow_intensity": 82}             # Neon Orange
]

def init_block_settings():
    """Create or update block settings"""
    print("🎨 Initializing Block Settings...")
    
    # Create tables
    init_db()
    
    with Session(engine) as session:
        for block_data in BLOCK_DEFAULTS:
            # Check if exists
            stmt = select(BlockSettings).where(BlockSettings.block_name == block_data["block_name"])
            existing = session.exec(stmt).first()
            
            if existing:
                print(f"   ✓ {block_data['block_name']} already exists")
            else:
                # Create new
                block = BlockSettings(
                    block_name=block_data["block_name"],
                    color=block_data["color"],
                    fill_opacity=0.15,
                    border_width=2,
                    glow_intensity=block_data["glow_intensity"],
                    show_boundary=True
                )
                session.add(block)
                print(f"   + Created {block_data['block_name']} → {block_data['color']}")
        
        session.commit()
    
    print("✅ Block settings initialized!\n")

if __name__ == "__main__":
    init_block_settings()
