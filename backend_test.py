#!/usr/bin/env python3
import requests
import sys
import time
from datetime import datetime

class ThemePreviewAPITester:
    def __init__(self, base_url="https://f7f35b78-dc12-44f6-8f55-acc5ff3d89b4.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
        
        result = {
            "test_name": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
        if details:
            print(f"    Details: {details}")

    def test_health_endpoint(self):
        """Test /api/health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "ok":
                    self.log_test("Health Endpoint", True, f"Status code: {response.status_code}, Response: {data}")
                    return True
                else:
                    self.log_test("Health Endpoint", False, f"Invalid response format: {data}")
                    return False
            else:
                self.log_test("Health Endpoint", False, f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Health Endpoint", False, f"Request failed: {str(e)}")
            return False

    def test_download_endpoint(self):
        """Test /api/download endpoint and verify binary files"""
        import zipfile
        import tempfile
        
        try:
            response = requests.get(f"{self.base_url}/api/download", timeout=30)
            
            if response.status_code != 200:
                self.log_test("Download Endpoint", False, f"Status code: {response.status_code}")
                return False
            
            # Check content type and size
            content_type = response.headers.get('content-type', '')
            content_length = len(response.content)
            
            # Expected size should be around 51KB
            if content_length < 40000 or content_length > 70000:
                self.log_test("Download ZIP Size", False, 
                            f"Unexpected size: {content_length} bytes (expected ~51KB)")
                return False
            
            self.log_test("Download ZIP Size", True, 
                        f"Size: {content_length:,} bytes (~{content_length/1024:.1f}KB)")
            
            if 'application/zip' not in content_type and 'application/octet-stream' not in content_type:
                self.log_test("Download Content-Type", False, f"Incorrect content-type: {content_type}")
                return False
            
            self.log_test("Download Content-Type", True, f"Content-Type: {content_type}")
            
            # Verify ZIP contents and binary files
            with tempfile.NamedTemporaryFile() as temp_zip:
                temp_zip.write(response.content)
                temp_zip.flush()
                
                try:
                    with zipfile.ZipFile(temp_zip.name, 'r') as zip_file:
                        # Check required files exist
                        required_files = ['body_LZ.bin', 'top.png', 'bottom.png', 'preview.png', 'info.smdh', 'README_BUILD.md']
                        zip_contents = zip_file.namelist()
                        
                        missing_files = [f for f in required_files if f not in zip_contents]
                        if missing_files:
                            self.log_test("ZIP File Contents", False, f"Missing files: {missing_files}")
                            return False
                        
                        self.log_test("ZIP File Contents", True, f"All required files present: {required_files}")
                        
                        # Verify body_LZ.bin binary format
                        body_lz_data = zip_file.read('body_LZ.bin')
                        if len(body_lz_data) == 0:
                            self.log_test("body_LZ.bin Format", False, "File is empty")
                            return False
                        
                        # Check LZ11 header (first byte should be 0x11)
                        if body_lz_data[0] != 0x11:
                            self.log_test("body_LZ.bin LZ11 Header", False, 
                                        f"First byte is 0x{body_lz_data[0]:02X}, expected 0x11")
                            return False
                        
                        # Check expected file size (~12604 bytes based on spec)
                        if len(body_lz_data) < 10000 or len(body_lz_data) > 15000:
                            self.log_test("body_LZ.bin Size", False, 
                                        f"Size {len(body_lz_data)} bytes, expected ~12604 bytes")
                            return False
                        
                        self.log_test("body_LZ.bin Format", True, 
                                    f"Valid LZ11 format: size {len(body_lz_data)} bytes, header 0x{body_lz_data[0]:02X}")
                        
                        # Verify info.smdh binary format  
                        info_smdh_data = zip_file.read('info.smdh')
                        if len(info_smdh_data) != 14016:
                            self.log_test("info.smdh Size", False, 
                                        f"Size {len(info_smdh_data)} bytes, expected exactly 14016 bytes")
                            return False
                        
                        # Check SMDH magic
                        if info_smdh_data[0:4] != b'SMDH':
                            self.log_test("info.smdh Magic", False, 
                                        f"Magic bytes: {info_smdh_data[0:4]}, expected b'SMDH'")
                            return False
                        
                        # Check for non-zero icon data at offset 0x2040
                        icon_data_offset = 0x2040
                        icon_sample = info_smdh_data[icon_data_offset:icon_data_offset+32]
                        if all(b == 0 for b in icon_sample):
                            self.log_test("info.smdh Icon Data", False, "Icon data at offset 0x2040 is all zeros")
                            return False
                        
                        self.log_test("info.smdh Format", True, 
                                    f"Valid SMDH: size 14016 bytes, magic 'SMDH', non-zero icon data")
                        
                        return True
                        
                except zipfile.BadZipFile:
                    self.log_test("ZIP File Validity", False, "Downloaded file is not a valid ZIP")
                    return False
                    
        except Exception as e:
            self.log_test("Download Endpoint", False, f"Request failed: {str(e)}")
            return False

    def test_static_assets_access(self):
        """Test if static assets are accessible"""
        assets = ["top.png", "bottom.png", "preview.png"]
        all_passed = True
        
        for asset in assets:
            try:
                response = requests.get(f"{self.base_url}/{asset}", timeout=10)
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    if 'image' in content_type:
                        self.log_test(f"Static Asset - {asset}", True, 
                                    f"Content-Type: {content_type}")
                    else:
                        self.log_test(f"Static Asset - {asset}", False, 
                                    f"Invalid content-type: {content_type}")
                        all_passed = False
                else:
                    self.log_test(f"Static Asset - {asset}", False, 
                                f"Status code: {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"Static Asset - {asset}", False, f"Request failed: {str(e)}")
                all_passed = False
        
        return all_passed

    def run_all_tests(self):
        """Run all backend tests"""
        print(f"🔍 Starting API tests for: {self.base_url}")
        print("=" * 60)
        
        # Test health endpoint
        health_ok = self.test_health_endpoint()
        
        # Test download endpoint with binary verification
        download_ok = self.test_download_endpoint()
        
        # Test static assets
        assets_ok = self.test_static_assets_access()
        
        # Summary
        print("\n" + "=" * 60)
        print(f"📊 Backend Test Summary:")
        print(f"   Tests passed: {self.tests_passed}/{self.tests_run}")
        print(f"   Success rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("✅ All backend tests passed!")
            return True
        else:
            print("❌ Some backend tests failed")
            print("\nFailed tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   - {result['test_name']}: {result['details']}")
            return False

def main():
    tester = ThemePreviewAPITester()
    success = tester.run_all_tests()
    
    # Return exit code
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    print(f"\nBackend testing completed with exit code: {exit_code}")
    sys.exit(exit_code)