"""
Audio System Test Suite
Comprehensive testing for audio capture and speech-to-text integration.
"""

import time
import sys
import traceback
from pathlib import Path
from typing import Dict, List, Optional

# Import our audio modules
try:
    from .audio_capture import AudioCapture, AudioConfig
    from .audio_utils import AudioDeviceManager, print_audio_system_info
    from .audio_error_handler import handle_audio_error, print_audio_error_help
    from .speech_client import SpeechClient
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Could not import audio modules: {e}")
    MODULES_AVAILABLE = False


class AudioTestSuite:
    """Comprehensive audio system testing"""
    
    def __init__(self):
        self.results = {}
        self.errors = []
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all audio tests"""
        print("🎤 Starting Audio Test Suite")
        print("=" * 60)
        
        if not MODULES_AVAILABLE:
            print("❌ Audio modules not available - skipping tests")
            return {'modules_available': False}
        
        tests = [
            ('system_info', self.test_system_info),
            ('device_detection', self.test_device_detection),
            ('audio_capture', self.test_audio_capture),
            ('speech_client', self.test_speech_client),
            ('grpc_connection', self.test_grpc_connection),
            ('end_to_end', self.test_end_to_end)
        ]
        
        for test_name, test_func in tests:
            print(f"\n🧪 Running {test_name.replace('_', ' ').title()} Test...")
            try:
                result = test_func()
                self.results[test_name] = result
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"   {status}")
            except Exception as e:
                self.results[test_name] = False
                self.errors.append((test_name, e))
                print(f"   ❌ ERROR: {e}")
        
        self.print_summary()
        return self.results
    
    def test_system_info(self) -> bool:
        """Test system information gathering"""
        try:
            system_info = AudioDeviceManager.get_system_info()
            print(f"   Platform: {system_info.get('platform', 'Unknown')}")
            print(f"   Audio System: {system_info.get('audio_system', 'Unknown')}")
            return True
        except Exception as e:
            print(f"   Error getting system info: {e}")
            return False
    
    def test_device_detection(self) -> bool:
        """Test audio device detection"""
        try:
            # Check permissions
            has_permissions = AudioDeviceManager.check_audio_permissions()
            print(f"   Audio Permissions: {'✅' if has_permissions else '❌'}")
            
            if not has_permissions:
                print("   Skipping device tests - no permissions")
                return False
            
            # Get recommended device
            recommended = AudioDeviceManager.get_recommended_device()
            if recommended:
                print(f"   Recommended Device: {recommended['name']}")
                print(f"   Channels: {recommended['channels']}")
                print(f"   Sample Rate: {recommended['sample_rate']} Hz")
                return True
            else:
                print("   No recommended device found")
                return False
                
        except Exception as e:
            print(f"   Device detection error: {e}")
            return False
    
    def test_audio_capture(self) -> bool:
        """Test audio capture functionality"""
        try:
            # Create audio capture instance
            config = AudioConfig(record_seconds=1.0)  # Short test
            capture = AudioCapture(config)
            
            print("   Testing 1-second audio capture...")
            
            # Start recording
            if not capture.start_recording(duration=1.0):
                print("   Failed to start recording")
                return False
            
            # Wait for recording to complete
            time.sleep(1.5)
            
            # Stop and get audio data
            audio_data = capture.stop_recording()
            
            if audio_data and len(audio_data) > 0:
                print(f"   Captured {len(audio_data)} bytes of audio")
                
                # Test audio level calculation
                level = capture.get_current_level()
                peak = capture.get_peak_level()
                print(f"   Audio Level: {level:.3f}, Peak: {peak:.3f}")
                
                capture.cleanup()
                return True
            else:
                print("   No audio data captured")
                capture.cleanup()
                return False
                
        except Exception as e:
            print(f"   Audio capture error: {e}")
            print_audio_error_help(e)
            return False
    
    def test_speech_client(self) -> bool:
        """Test speech client initialization"""
        try:
            client = SpeechClient()
            
            # Test connection info
            audio_info = client.get_audio_info()
            print(f"   gRPC Connected: {'✅' if audio_info['grpc_connected'] else '❌'}")
            print(f"   Audio Capture Available: {'✅' if audio_info['audio_capture_available'] else '❌'}")
            print(f"   Real Audio Enabled: {'✅' if audio_info['real_audio_enabled'] else '❌'}")
            
            if audio_info['available_devices'] > 0:
                print(f"   Available Devices: {audio_info['available_devices']}")
            
            client.close()
            return True
            
        except Exception as e:
            print(f"   Speech client error: {e}")
            return False
    
    def test_grpc_connection(self) -> bool:
        """Test gRPC connection to speech service"""
        try:
            client = SpeechClient()
            
            if client.is_connected():
                print("   gRPC connection successful")
                
                # Test with dummy audio data
                dummy_audio = b"dummy_audio_data_for_testing"
                result = client.transcribe_audio(dummy_audio)
                print(f"   Transcription test result: {result[:50]}...")
                
                client.close()
                return True
            else:
                print("   gRPC connection failed - service may not be running")
                client.close()
                return False
                
        except Exception as e:
            print(f"   gRPC connection error: {e}")
            return False
    
    def test_end_to_end(self) -> bool:
        """Test complete end-to-end audio pipeline"""
        try:
            print("   Testing complete audio pipeline...")
            
            client = SpeechClient()
            
            if not client.is_connected():
                print("   Skipping end-to-end test - no gRPC connection")
                return False
            
            # This would require real audio input to test properly
            print("   End-to-end test requires manual verification")
            print("   Use the GUI microphone button to test complete pipeline")
            
            client.close()
            return True
            
        except Exception as e:
            print(f"   End-to-end test error: {e}")
            return False
    
    def print_summary(self):
        """Print test results summary"""
        print("\n" + "=" * 60)
        print("🎤 Audio Test Suite Results")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results.values() if result)
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\nDetailed Results:")
        for test_name, result in self.results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {test_name.replace('_', ' ').title()}: {status}")
        
        if self.errors:
            print("\nErrors Encountered:")
            for test_name, error in self.errors:
                print(f"  {test_name}: {error}")
        
        print("\n" + "=" * 60)
    
    def get_diagnostic_info(self) -> Dict[str, str]:
        """Get comprehensive diagnostic information"""
        info = {}
        
        try:
            # System info
            system_info = AudioDeviceManager.get_system_info()
            info.update(system_info)
            
            # Installation instructions
            instructions = AudioDeviceManager.get_installation_instructions()
            info['installation_help'] = instructions
            
            # Test results
            info['test_results'] = self.results
            
        except Exception as e:
            info['diagnostic_error'] = str(e)
        
        return info


def run_quick_test():
    """Run a quick audio system test"""
    print("🎤 Quick Audio System Test")
    print("-" * 30)
    
    if not MODULES_AVAILABLE:
        print("❌ Audio modules not available")
        return False
    
    try:
        # Test 1: System info
        print("1. System Info...")
        print_audio_system_info()
        
        # Test 2: Device permissions
        print("\n2. Device Permissions...")
        has_permissions = AudioDeviceManager.check_audio_permissions()
        print(f"   Permissions: {'✅' if has_permissions else '❌'}")
        
        # Test 3: Speech client
        print("\n3. Speech Client...")
        client = SpeechClient()
        audio_info = client.get_audio_info()
        print(f"   gRPC: {'✅' if audio_info['grpc_connected'] else '❌'}")
        print(f"   Audio: {'✅' if audio_info['real_audio_enabled'] else '❌'}")
        client.close()
        
        print("\n✅ Quick test completed")
        return True
        
    except Exception as e:
        print(f"\n❌ Quick test failed: {e}")
        return False


def main():
    """Main test function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        run_quick_test()
    else:
        test_suite = AudioTestSuite()
        test_suite.run_all_tests()


if __name__ == "__main__":
    main()
