# Quick Fix Steps - Enable MT7925 Bluetooth

## Step 1: Load the Bluetooth Driver

```bash
sudo modprobe btmtk
```

This loads the MediaTek Bluetooth driver that's already compiled into your kernel.

## Step 2: Verify It Worked

```bash
hciconfig -a
```

**Expected output**: Should show an adapter like `hci0: Type: Primary  Bus: PCIe`

**If empty**: Driver didn't load, go to Troubleshooting below

## Step 3: Check BlueZ

```bash
bluetoothctl list
```

**Expected output**: Should show at least one adapter

**If empty**: Driver loaded but BlueZ not recognizing it, go to Troubleshooting

## Step 4: Test Bluetooth Discovery

```bash
bluetoothctl
> power on
> scan on
```

**Expected**: Should start discovering Bluetooth devices

## Step 5: Test Your GUI

Launch your GTK4 app and check the Bluetooth tab. It should:
- Not freeze
- Show discovered devices
- Allow pairing/connection

---

## Troubleshooting

### If `modprobe btmtk` fails

```bash
# Check if the module exists
ls -la /lib/modules/$(uname -r)/kernel/drivers/bluetooth/btmtk.ko.zst

# If it exists, try with verbose output
sudo modprobe -v btmtk

# Check kernel logs
journalctl -xe | grep -i "btmtk\|bluetooth"
```

### If driver loads but hciconfig shows nothing

```bash
# Check if the device is being detected
lspci | grep -i mediatek

# Check if firmware is present
ls -la /lib/firmware/mediatek/mt7925/

# Check kernel logs for firmware errors
dmesg | grep -i "mt7925\|bluetooth\|firmware" | tail -20
```

### If BlueZ still doesn't see the adapter

```bash
# Restart BlueZ daemon
sudo systemctl restart bluetooth

# Check BlueZ logs
journalctl -u bluetooth -n 50

# Check if adapter is in DOWN state
bluetoothctl
> list
> info <adapter_address>
> power on
```

### If BIOS has Bluetooth disabled

1. Restart your system
2. Enter BIOS (usually DEL or F2 during boot)
3. Find "Integrated Peripherals" or "Onboard Devices"
4. Look for "Bluetooth" or "Wireless" settings
5. Enable Bluetooth
6. Save and exit
7. Try `modprobe btmtk` again

---

## If Nothing Works

The MT7925 Bluetooth support in kernel 6.14.0-1015-oem might be incomplete. Options:

1. **Upgrade kernel**: Try kernel 6.15+ if available
2. **Check ASUS support**: Look for MT7925 driver updates
3. **Use mock Bluetooth**: Create mock D-Bus objects for testing
4. **Get USB adapter**: Use external Bluetooth adapter ($15-30)

---

## Expected Result

Once the driver loads and BlueZ recognizes the adapter:

- ✅ Bluetooth tab shows devices
- ✅ No UI freezes
- ✅ Device discovery works
- ✅ Pairing/connection works
- ✅ Your code works as-is (no refactoring needed)

---

## Important Note

**Your code is not the problem.** The D-Bus timeout is expected when there's no Bluetooth adapter. Once the driver loads, everything will work.


