# LNA Testing Setup Guide

To fully characterize a Low Noise Amplifier (LNA) or any RF component, you need to measure its Gain, Impedance Matching, Linearity, and Noise Figure. Here is how to use the Signal Generator, Spectrum Analyzer, and Vector Network Analyzer (VNA) for these tests.

## 1. Vector Network Analyzer (VNA) Setup
**Purpose:** Measure S-parameters: Gain ($S_{21}$), Input Return Loss ($S_{11}$), Output Return Loss ($S_{22}$), and Isolation ($S_{12}$).

**Connections:**
1. Connect **VNA Port 1** to the **LNA RF Input**.
2. Connect **VNA Port 2** to the **LNA RF Output**.
3. Connect a DC Power Supply to the LNA's power terminals.
4. *Important:* Ensure the VNA output power is set low enough (e.g., -30 dBm) so it does not saturate the LNA during the sweep.

## 2. Signal Generator & Spectrum Analyzer Setup
**Purpose:** Measure Linearity (1-dB Compression Point $P_{1dB}$, Third-Order Intercept $IP_3$) and Harmonics.

**Connections:**
1. Connect the **Signal Generator (SG) RF Output** to the **LNA RF Input**.
2. Connect the **LNA RF Output** to the **Spectrum Analyzer (SA) RF Input**.
3. Connect the DC Power Supply to the LNA.

**How to Test $P_{1dB}$:**
- Set the SG to the desired operating frequency (e.g., 2.4 GHz).
- Start with a very low input power (e.g., -40 dBm).
- Read the output power peak on the SA.
- Increase the SG power in 1 dB steps. The SA reading should also increase by 1 dB.
- When the SA reading increases by 0 dB instead of 1 dB (meaning the gain has dropped by 1 dB), you have reached the input 1-dB Compression Point.

## 3. Important Precautions (Read Before Testing!)
- **DC Blocks:** If the LNA does not have internal DC blocking capacitors, always place external DC Blocks on the RF input/output to prevent DC voltage from damaging the expensive VNA, Signal Generator, or Spectrum Analyzer.
- **Attenuators:** If the LNA has very high gain, place a fixed attenuator (e.g., 10 dB or 20 dB) at the Spectrum Analyzer input to prevent burning out its sensitive front-end mixer.
