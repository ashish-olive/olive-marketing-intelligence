#!/usr/bin/env python3
"""
Package deployment bundle for local use
Combines database + trained models into a single zip file
"""
import zipfile
from pathlib import Path
import shutil
import os


def package_deployment():
    print("="*60)
    print("PACKAGING DEPLOYMENT BUNDLE")
    print("="*60)
    
    # Create temp directory
    temp_dir = Path('deployment_temp')
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()
    
    # Copy database
    print("\n[1/3] Copying database...")
    db_path = Path('instance/marketing.db')
    if db_path.exists():
        shutil.copy(db_path, temp_dir / 'marketing.db')
        db_size = db_path.stat().st_size / (1024 * 1024)
        print(f"  ✓ Database copied ({db_size:.1f} MB)")
    else:
        print("  ⚠️  Database not found! Run generate_data.py first.")
        return
    
    # Copy trained models
    print("\n[2/3] Copying trained models...")
    models_dir = temp_dir / 'trained_models'
    models_dir.mkdir(exist_ok=True)
    
    source_models_dir = Path('ml-models/trained_models')
    if source_models_dir.exists():
        model_count = 0
        total_size = 0
        
        for model_file in source_models_dir.glob('*.pth'):
            shutil.copy(model_file, models_dir / model_file.name)
            size = model_file.stat().st_size / (1024 * 1024)
            total_size += size
            model_count += 1
            print(f"  ✓ {model_file.name} ({size:.1f} MB)")
        
        # Copy metadata
        metadata_file = source_models_dir / 'metadata.json'
        if metadata_file.exists():
            shutil.copy(metadata_file, models_dir / 'metadata.json')
            print(f"  ✓ metadata.json")
        
        print(f"\n  Total: {model_count} models ({total_size:.1f} MB)")
    else:
        print("  ⚠️  No trained models found. Run train_all.py first.")
        print("  (App will work with fallback predictions)")
    
    # Create zip
    print("\n[3/3] Creating zip file...")
    zip_path = 'deployment_package.zip'
    if Path(zip_path).exists():
        os.remove(zip_path)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in temp_dir.rglob('*'):
            if file.is_file():
                arcname = file.relative_to(temp_dir)
                zipf.write(file, arcname)
                print(f"  + {arcname}")
    
    # Cleanup
    shutil.rmtree(temp_dir)
    
    # Stats
    zip_size = Path(zip_path).stat().st_size / (1024 * 1024)
    
    print("\n" + "="*60)
    print("PACKAGING COMPLETE!")
    print("="*60)
    print(f"\nPackage: {zip_path} ({zip_size:.1f} MB)")
    print("\nContents:")
    print("  - marketing.db (database)")
    print("  - trained_models/*.pth (ML models)")
    print("  - trained_models/metadata.json (model info)")
    print("\n" + "="*60)
    print("NEXT STEPS:")
    print("="*60)
    print("\n1. Download this file to your local machine")
    print("\n2. Extract the package:")
    print("   unzip deployment_package.zip")
    print("   mv marketing.db instance/")
    print("   mv trained_models/* ml-models/trained_models/")
    print("\n3. Run the app locally:")
    print("   cd backend && python app.py")
    print("   cd frontend && npm start")
    print("\n" + "="*60)


if __name__ == '__main__':
    package_deployment()
