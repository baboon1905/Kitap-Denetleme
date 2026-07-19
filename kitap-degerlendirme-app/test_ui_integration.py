#!/usr/bin/env python3
"""
Test React UI - Upload and Analysis Integration
"""
import requests
import json

API_BASE = 'http://localhost:5000/api'

def test_upload_and_analyze():
    """Upload PDF and run analysis"""
    
    print("=" * 60)
    print("🧪 React UI Integration Test")
    print("=" * 60)
    
    try:
        file_path = 'uploads/03_cokbilmis_alingan.pdf'
        
        # 1. Upload
        print("\n📤 Step 1: Uploading PDF...")
        with open(file_path, 'rb') as f:
            files = {'pdf': f}  # NOTE: Field name is 'pdf' not 'dosya'
            upload_resp = requests.post(f'{API_BASE}/yukleme', files=files, timeout=15)
        
        if upload_resp.status_code != 200:
            print(f"❌ Upload failed: {upload_resp.status_code}")
            print(f"   Response: {upload_resp.text}")
            return
        
        upload_data = upload_resp.json()
        if not upload_data.get('basarili'):
            print(f"❌ Upload error: {upload_data.get('hata')}")
            return
        
        dosya_adi = upload_data.get('kitap_adi')
        print(f"✅ File uploaded: {dosya_adi}")
        print(f"   Path: {upload_data.get('dosya_yolu')}")
        
        # 2. Analyze
        print("\n🔍 Step 2: Analyzing...")
        dosya_yolu = upload_data.get('dosya_yolu')
        analysis_resp = requests.post(f'{API_BASE}/degerlendir',
            json={
                'dosya_yolu': dosya_yolu,  # Must be 'dosya_yolu' not 'dosya'
                'profil': 'hibrit',
                'yas_grubu': '9-12'
            },
            timeout=15)
        
        if analysis_resp.status_code != 200:
            print(f"❌ Analysis failed: {analysis_resp.status_code}")
            print(f"   Response: {analysis_resp.text}")
            return
        
        analysis = analysis_resp.json()
        if not analysis.get('basarili'):
            print(f"❌ Analysis error: {analysis.get('hata')}")
            return
        
        sonuc = analysis.get('analiz_sonucu', {})
        print(f"✅ Analysis complete!")
        print(f"   Risk Score: {sonuc.get('final_skor', 'N/A')}/100")
        print(f"   Decision: {sonuc.get('karar', {}).get('seviye', 'N/A')} {sonuc.get('karar', {}).get('simge', '')}")
        print(f"   Categories Found: {len(sonuc.get('kategori_bulgulari', {}))}")
        
        # 3. Generate Report
        print("\n📄 Step 3: Generating PDF Report...")
        report_resp = requests.post(f'{API_BASE}/rapor',
            json={
                'dosya_yolu': dosya_yolu,
                'profil': 'hibrit',
                **sonuc
            },
            timeout=15)
        
        if report_resp.status_code == 200:
            report_path = f'test_report_{dosya_adi.replace(".pdf", "")}.pdf'
            with open(report_path, 'wb') as rf:
                rf.write(report_resp.content)
            print(f"✅ Report generated: {report_path}")
            print(f"   Size: {len(report_resp.content)} bytes")
        else:
            print(f"⚠️  Report generation failed: {report_resp.status_code}")
        
        print("\n" + "=" * 60)
        print("✅ SYSTEM OPERATIONAL - Ready for Web UI Testing!")
        print("=" * 60)
        print("\n🌐 Open http://localhost:3002 in browser")
        print("📤 Click 'Yükle' to upload a PDF")
        print("🔍 Click 'Analiz Et' to analyze")
        print("=" * 60)
        
    except FileNotFoundError as e:
        print(f"❌ Test file not found: {file_path}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask backend (http://localhost:5000)")
        print("   Make sure 'python app.py' is running")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_upload_and_analyze()
