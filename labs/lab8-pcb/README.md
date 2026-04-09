# Printed Circuit Board

## Introduction

This lab involves designing a bandpass filter and developing a standalone printed circuit board (PCB). After completing this lab, you should understand the filter design process and also gain experience using kicad.

## Part 1 - Filter Design (50%)

Using <https://rf-tools.com/lc-filter/> (or any other filter design tool that you like), design a bandpass filter for WSPR which meets the following specifications using the minimum number of components:

 1. maximum ripple in WSPR region (7.0400-7.0402 MHz) 0.1 dB
 1. center frequency 7.0401 MHz
 1. min -3dB attenuation +/- 0.25 MHz from center frequency and -50dB at 10 MHz
 1. input and output impedance 50 ohms
 1. E96 capacitor and inductor (1% tolerance) values.

Export the design from your filter design program and simulate using LTspice. Run a Monte Carlo simulation and verify that the design will meet the specifications even though the component values will vary within their 1% range.

Create LTspice plots that demonstrate Specification 1 and 3 can be met assuming random variations of the capacitor and inductor values within the stated tolerance.

## Part 2 - PCB Layout (50%)

Make a Kicad design of a printed circuit board that implements this filter. For input and output, use PCB mount SMA connectors. Use 1206 surface mount components where possible. Create the Gerber files that could be used for manufacture. For the input and output connectors, use the SMA_Amphenol_132289_EdgeMount footprint. Your board should be 2 sided, use the default Kicad clearances, and roughly square in aspect ratio.

Place the initials of your group members and the date on the front silk screen. Your PCB design must match your schematic and be free of any errors or warnings in the Design Rule Check (DRC). You should also select the "Test for parity between PCB and schematic" option in your DRC.

In your lab book you should include:

 1. schematic (pdf)
 1. PCB layout (plot of all layers)
 1. screen shot showing dimensions of your PCB. Smaller PCBs will receive higher marks (but need to be correct).

