# Optimal Design of a Dual-Active-Bridge DC–DC Converter

**Dibakar Das**, *Student Member, IEEE*, and **Kaushik Basu**, *Senior Member, IEEE*

*IEEE Transactions on Industrial Electronics, Vol. 68, No. 12, December 2021*

DOI: [10.1109/TIE.2020.3044781](https://doi.org/10.1109/TIE.2020.3044781)

---

## Abstract

This article presents a systematic design procedure for a dual-active-bridge (DAB) dc–dc converter. Design of a DAB converter involves determination of two key parameters, i.e., transformer turns ratio and the series inductance value. Existing literature addresses this problem through numerical optimization, which is computation intensive and does not provide much insight. In general, loss is minimized by applying equal weightage to all operating conditions, which may not be practical. Given an operating power range, terminal voltage range, and switching frequency, this article presents a way to optimally select the design variables through analytical solution of a constrained optimization problem. Analysis is carried out in the time domain, and an optimal triple-phase-shift modulation strategy is considered that ensures minimum inductor rms current and soft switching. The choice of the design parameters results in minimization of the worst-case inductor rms current over the entire operating range of the converter, which leads to both efficiency and size optimization. A procedure for selection of devices and filter capacitors and design of magnetics is given. A 2.6-kW experimental prototype is designed to validate the theoretical analysis.

**Index Terms:** Dual active bridge (DAB), optimal design, RMS current minimization, soft switching, triple-phase-shift (TPS) modulation.

---

## Nomenclature

| Symbol | Description |
|--------|-------------|
| V₁ | Voltage of the controlled port |
| V₂ | Voltage of the uncontrolled port |
| i_L | Instantaneous inductor current |
| I_rms | Actual value of inductor rms current |
| i_rms | Scaled value of inductor rms current |
| P | Average power transferred between the dc ports |
| p | Scaled value of average transferred power |
| f_s | Switching frequency of the converter |
| n | Turns ratio of the transformer |
| L | Total series inductance of the DAB converter |
| d₁ | Duty cycle of primary voltage waveform |
| d₂ | Duty cycle of secondary voltage waveform |
| δ | Phase shift between primary and secondary voltage waveforms |
| m | Voltage conversion ratio |

---

## I. Introduction

Dual active bridge (DAB) converters are a desirable choice in dc–dc power conversion, since they have several beneficial features such as galvanic isolation, bidirectional power flow capability, soft switching leading to high efficiency, and power density [1]. These converters are used in several applications such as dc microgrids, battery chargers, solid-state transformers, etc.

In the DAB topology, two H-bridge converters apply square waveforms to transformer primary and secondary windings in series with an inductor. A phase shift is introduced between the waveforms for power transfer [2]. This modulation strategy is known as single-phase-shift (SPS) strategy in the literature. Later, it was found that introducing duty modulation in primary and secondary voltages can lead to several advantages [3]. This three-degree-of-freedom modulation (two duty cycles and phase shift) is known as triple-phase-shift (TPS) strategy in the literature [3]. The TPS strategy is considered in this article.

Several methods exist in literature which address the optimal modulation problem based on minimization of a given objective function. In such problems, for a specified operating condition (power, voltage, and switching frequency) and a given design (transformer turns ratio and series inductance value), the objective is to determine the TPS modulation parameters, which will minimize power loss. For loss minimization, one popular approach is using fundamental approximation [4]–[7] of the voltage and current waveform and minimize the circulating [4], [5] or reactive component [6], [7] of the inductor current. Although this approach leads to a simpler analysis, the approximations may not be valid over a wide operating range of the converter. A more general method that results in accurate prediction over a wide range of operation is to use time-domain expressions for power and inductor current [3], [8]–[10].

Considering time-domain analysis, the objective function for minimization may be inductor rms current [8]–[10], peak current [11]–[15], soft switching [3], [16], or total loss [17]–[19]. Out of the above alternatives for the objective function, the rms of the inductor current with soft switching is a suitable candidate for optimization because it represents the conduction losses in the devices and the magnetic components, which form a major fraction of the total loss of the converter [8]. Moreover, reducing the rms of inductor current also implies reduction of peak currents and capacitor ripple current ratings.

Several approaches for minimization of rms currents through time-domain exact analysis can be found in the literature. A numerical approach for choosing optimal TPS parameters can be found in [8]. The proposed strategy has three regions of operation based on the power output of the converter. A more formal treatment of the rms current minimization problem and an analytical solution can be found in [10]. Though soft switching is not included in the problem formulation, it is shown that the results satisfy the soft switching constraints.

In a typical dc–dc converter, the voltage at one port is tightly regulated despite variations in the other port voltage. The design specifications include voltage at the regulated port, the range of unregulated port voltage, range of operating power, and the switching frequency [20]–[22]. Design of the DAB dc–dc converter involves determining the turns ratio of the transformer and the series inductance [19], [23], [24]. Based on the worst-case stresses on the components, the design of magnetic components and selection of switches and capacitors can then be carried out.

In [23], the transformer turns ratio is chosen to obtain voltage conversion ratio of unity at the maximum value of unregulated voltage while applying the SPS strategy for power transfer. The inductance value is chosen to provide good controllability. This method is simple and widely used, but it does not attempt to minimize rms inductor current or losses. In [24], a numerical design approach is adopted for selection of optimal transformer turns ratio and inductance value for minimization of rms inductor current averaged over several operating voltages at fixed power. The same method is used to minimize peak inductor current or total power loss, which provide separate design parameter values. The SPS strategy is considered for the analysis. It is well known in the DAB literature [3], [8] that SPS results in large rms currents and loss of zero-voltage switching (ZVS) for wide variation of voltage and power. In [19], a numerical approach similar to that in [24] is taken, but TPS with ZVS is considered, and average efficiency is used as an objective function. Search is carried over a range of operating points resulting due to variations in unregulated port voltage and power.

Total loss or efficiency as an objective function is complex and requires knowledge of device- and magnetics-related parameters, which are usually not known before the basic design is completed. In the numerical search technique [19], [24], the search space is divided into discrete points, and the objective function is evaluated at each point to identify the optimum. This process is computation extensive, requires programming effort, and does not provide much insight. Applying equal weightage to each operating point may not be practical.

This article presents a novel analytical design procedure for a DAB dc–dc converter. The design specifications are the regulated port voltage, range of unregulated voltage, operating power range, and switching frequency. The optimal TPS strategy is considered for the analysis, which results in minimum rms current while ensuring soft switching. For accurate results, the minimization problem is formulated considering time-domain analysis. Though it may seem obvious, it is established that maximum rms current with an optimal TPS strategy flows at maximum power. This conclusion is independent of the choice of design parameters and the variation of voltage at the unregulated port. Minimization of the maximum rms current experienced by the converter over the operating range leads to optimal sizing of devices, filter capacitors, and magnetics. A constrained optimization problem to minimize worst-case inductor rms current is formulated and then solved analytically. The first-order necessary conditions are applied on the objective function to obtain algebraic equations for optimal variables. Since a closed-form expression does not exist for one of the equations, a numerical root-finding technique is used to find the optimal value. A polynomial curve fit is then provided for selection of the inductance value, which reduces the computation effort. The solution thus obtained provides optimal values of the design variables (transformer turns ratio and inductance value). The proposed solution results in the maximum rms current (at maximum power) to remain close to its minimum value despite variations of voltage at the uncontrolled port. The optimal TPS strategy can be applied to the optimal design to obtain minimum rms currents and soft switching over the entire operating range of the converter. The key steps in selecting the power devices, filter capacitors, and design of magnetics are also presented.

The rest of this article is organized as follows. Section II describes the design problem and modeling of the converter for various zones of operation. An optimization problem is formulated for rms current minimization. A systematic procedure is discussed for the choice of design parameters. Section III demonstrates the experimental results with the proposed design strategy. Section IV concludes this article.

---

## II. Analysis and Optimal Design

Consider the DAB dc–dc converter transferring power P between dc voltage sources V₁ and V₂ and switching at frequency f_s. The two H-bridge converters convert the dc voltages V₁ and V₂ to duty-modulated square waveforms v_ab and v_cd, respectively. These waveforms are then applied to a transformer connected in series with an inductor. The switches of the H-bridge converters are considered ideal, and the effect of transformer magnetizing inductance is neglected in the analysis. The inductor L is the transformer leakage inductance along with the external inductance. The converter can thus be equivalently replaced by two voltage sources and an inductor L. The power transfer between dc ports is carried out by introducing a phase shift between v_ab and v_cd.

A DAB converter can be modulated with three degrees of freedom. The primary and secondary voltage waveforms can be duty modulated. The pulsewidths are decided by d₁T_s/2 and d₂T_s/2 for primary and secondary voltages, respectively. The time shift δT_s/4 is provided for power transfer, where T_s = 1/f_s. The duty cycles d₁, d₂ ∈ [0, 1]. The phase shift ranges between −T_s/4 and T_s/4, which corresponds to δ ∈ [−1, 1]. δ > 0 results in power transfer from V₁ to V₂.

### A. Problem Description

Consider a DAB converter with the following specifications:
- Port 1 Voltage: V₁, switching frequency: f_s
- Port 2 Voltage: V₂min ≤ V₂ ≤ V₂max
- Power Rating: P_min ≤ P ≤ P_max

The above problem represents a scenario where one of the dc voltages (V₁) is tightly regulated despite variations of V₂. The converter load may also vary between two known limits. Converter design involves determination of the transformer turns ratio n and the value of series inductance L. After the design, the operation problem involves finding the modulation strategy (d₁, d₂, and δ) for a given P and V₂. The specifications of inductor, transformer, switches, and capacitor can then be determined based on worst-case operating conditions. The converter design should be carried out such that the maximum value of inductor rms current I_rms is minimized over the entire operating range (considering variations in P and V₂) of the converter. Moreover, ZVS should be ensured for the entire operating region of the converter.

### B. Converter Modeling

The voltage conversion ratio is defined as:

$$m = \frac{n_1 V_2}{n_2 V_1} = \frac{nV_2}{V_1} \tag{1}$$

where n₁ and n₂ are the number of turns in the transformer windings.

For a given n and the variation of V₂ described above, m varies between m_min := nV₂min/V₁ and m_max := nV₂max/V₁. With the defined conversion ratio, the voltage levels in v′_cd := nv_cd are ±mV₁ and 0. Note that the voltage levels in v_ab are ±V₁ and 0.

The inductor current can be described by:

$$L\frac{di_L}{dt} = v_{ab} - nv_{cd} \tag{2}$$

Since the primary and secondary pulsewidths are proportional to T_s, the inductor current magnitude is proportional to (V₁T_s/L) or (V₁/2πf_sL). Scaling the time axis with θ = 2πf_st, the inductor current at any time instant can be written as a product of V₁/2πf_sL and a proportionality factor i(m, d₁, d₂, δ, θ). The actual rms current I_rms can then be written as:

$$I_{rms} = \frac{V_1}{2\pi f_s L} \sqrt{\frac{1}{2\pi}\int_0^{2\pi} i^2\, d\theta} = \frac{V_1}{2\pi f_s L} i_{rms}(m, d_1, d_2, \delta) \tag{3}$$

Instantaneous power is the product of v_ab and the inductor current, and hence will be proportional to V₁²/2πf_sL with a proportionality factor that is a function of m, d₁, d₂, and δ. The average power over a switching cycle can be written as:

$$P = \frac{V_1^2}{2\pi f_s L} \times p(m, d_1, d_2, \delta) \tag{4}$$

#### 1) Converter Operating Zones

The range of values that d₁, d₂, and δ can assume is between 0 and 1. So, each feasible point (d₁, d₂, δ) belongs to a unit cube. This unit cube can be divided into five different operating zones, where the expressions for p and i_rms are different because the inductor voltage has different patterns [3]. Considering the transformation θ = 2πf_st to (2), the dynamics in i can be described by:

$$\frac{di}{d\theta} = v_L(\theta) \tag{5}$$

where v_L(θ) := (v_ab − v′_cd)/V₁ is the scaled inductor voltage.

For operation of the converter in zone V, considering the value of i at θ = 0 as i₀, the values i₀–i₅ can be determined as functions of m, d₁, d₂, and δ:

$$i_0 = \frac{\pi}{2}(m - d_1 - m\delta)$$
$$i_1 = \frac{\pi}{2}(2m - md_1 - d_1 - m\delta)$$
$$i_2 = \frac{\pi}{2}(\delta + d_2 + md_2 - 2)$$
$$i_3 = \frac{\pi}{2}(\delta - d_2 + md_2)$$
$$i_4 = \frac{\pi}{2}(d_1 - md_1 + m\delta)$$
$$i_5 = -\frac{\pi}{2}(m - d_1 - m\delta) \tag{7}$$

#### 2) Conditions for Soft Switching

Consider that the converter is operating in zone V and undergoing the switching transition at θ = θ₁. At this instant, switch S₂ is turning OFF and switch S₁ is turned ON after dead time. Assume that the current i₁ at θ₁ is less than zero. This implies that switch S₂ was conducting prior to its turn-OFF, and thus v_C2 = 0. On removing gate pulse for S₂, the inductor current quickly shifts to the capacitors C₂ and C₁, charging and discharging them, respectively. The channel current quickly reduces before voltage v_C2 increases, and hence, it reduces turn-OFF loss of S₂. Once the voltage v_C1 reduces to zero, the diode D₁ starts to conduct. Turning ON the switch after this instant will lead to ZVS turn-ON of S₁. Thus, i₁ should be less than zero for soft switching, which means (d₁ − 2m + mδ + md₁) > 0.

**Table I: ZVS Constraints for Different Operating Zones**

| Zone | Constraint 1 | Constraint 2 | Constraint 3 | Constraint 4 |
|------|-------------|-------------|-------------|-------------|
| Zone I | (d₁ − d₂m) > 0 | (δ − d₂ + d₂m) > 0 | (d₂ + δ − d₂m) < 0 | |
| Zone II | (d₁ − d₂m) < 0 | (d₁m − d₁ + mδ) < 0 | (d₁ − d₁m + mδ) > 0 | |
| Zone III | **(d₁ − d₂m) > 0** | (d₂m − d₂ + δ) > 0 | (d₁m − d₂ + mδ) > 0 | **(d₁ − d₂m) < 0** |
| Zone IV | **(d₁ − d₂m) > 0** | (d₁ + d₂m) > 0 | **(d₁ − d₂m) < 0** | |
| Zone V | (d₁ − 2m + mδ + md₁) > 0 | (d₂ + δ + md₂ − 2) > 0 | (δ − d₂ + d₂m) > 0 | (d₁ − d₁m + mδ) > 0 |

*Note: Inequalities in bold cannot be simultaneously satisfied in zones III and IV.*

From Table I, it can be concluded that ZVS conditions can be simultaneously satisfied in zones I, II, and V only.

The scaled power expressions are:

$$p_{zI} = 0.5m\pi\delta d_2$$
$$p_{zII} = 0.5m\pi\delta d_1$$
$$p_{zV} = 0.25m\pi\left[1 - (1-d_1)^2 - (1-d_2)^2 - (1-\delta)^2\right] \tag{8}$$

The inductor rms current expressions are:

$$i^2_{rms,zI} = \frac{\pi^2}{12}\left[-2d_1^3 + 3d_1^2d_2m + 3d_1^2 - 6d_1d_2m - 2d_2^3m^2 + d_2^3m + 3d_2^2m^2 + 3d_2\delta^2m\right]$$

$$i^2_{rms,zII} = \frac{\pi^2}{12}\left[d_1^3m - 2d_1^3 + 3d_1^2 + 3d_1d_2^2m - 6d_1d_2m + 3d_1\delta^2m - 2d_2^3m^2 + 3d_2^2m^2\right]$$

$$i^2_{rms,zV} = \frac{\pi^2}{12}\bigl[-2d_1^3 - 3d_1^2\delta m + 3d_1^2m + 3d_1^2 + 6d_1\delta m - 6d_1m - 2d_2^3m^2 - 3d_2^2\delta m$$
$$+ 3d_2^2m^2 + 3d_2^2m + 6d_2\delta m - 6d_2m - \delta^3m + 3\delta^2m - 6\delta m + 4m\bigr] \tag{9}$$

### C. Optimal Modulation Strategy

In general, the inductor rms current is a function of n, L, V₁, V₂, P, d₁, d₂, and δ. In the design problem, V₁ and f_s are fixed. Since n and V₂ both appear to impact I_rms and P as a product m = (nV₂/V₁), their variation can be represented as m. For one such given operating point (V₂ and P) and given n and L, it is possible to find d₁, d₂, and δ so that I_rms is minimized. This optimization problem, where (3) is the objective function with (4) and ZVS conditions as the constraints, is solved in [10]. The solution is known as the optimal modulation strategy. Using (3) and (4), the problem can be written as:

$$\min_{\substack{0 \le d_1, d_2, \delta \le 1,\, \text{ZVS} \\ p = P \times (2\pi f_s L)/V_1^2 = p|_m(d_1,d_2,\delta)}} \frac{i_{rms}|_m(d_1, d_2, \delta)}{1} \tag{10}$$

The solution depends on both m and p. For any given m, p must be smaller than mπ/4 for a solution of (10) to exist. The solution leads to three regions of operation [10]:

**Table II: Boundary Power Levels [10]**

| | p_c1 | p_c2 |
|---|------|------|
| m ≤ 1 | πm²(1−m)/2 | (1−m²)π/2m · (−1 + 1/√(1−m²)) |
| m > 1 | π(m−1)/2m | mπ/2 · (1 − m² + m√(m²−1)) |

**Table III: Optimum Modulation Parameters [10]**

| | p ∈ [0, p_c1] | p ∈ [p_c1, p_c2] |
|---|---------------|-----------------|
| **m ≤ 1** | d₁ = √(2p/((1−m)π)), d₁ = md₂, δ = (1−m)d₂ | d₂ = 1, πd₁(1−δ) = πm(2d₁ − d₁²) − 2p, δ = 1 − √(2d₁ − d₁² − 4p/mπ) |
| **m > 1** | d₁ = md₂, d₂ = √(2p/(πm(m−1))), δ = (m−1)d₂ | d₁ = 1, πd₂(1−δ) = π/m(2d₂ − d₂²) − 2p/m², δ = 1 − √(2d₂ − d₂² − 4p/mπ) |

Beyond power levels of p_c2, the converter operates with the conventional phase shift strategy (d₁ = 1, d₂ = 1). The value of δ is given by δ = 1 − √(1 − 4p/mπ).

For any fixed m and any arbitrary choice of L (provided p_max ≤ mπ/4 is ensured), the value of i_rms (hence I_rms) monotonically increases as p (or P) is increased. Thus, I_rms is maximum when P = P_max. It is now established that once m and L are fixed, the maximum value of rms current always occurs at P_max.

### D. Design Problem Formulation

At this point, we restate the design problem: (1) V₁ and f_s are known and fixed quantities; (2) n and V₂ appear as a product in (3) and (4), which is represented by m; and (3) m and L need to be determined so that rms inductor current I_rms is minimized for P = P_max. Substituting L (using P = P_max in (4)) into (3):

$$I_{rms} = \frac{i_{rms}(m, d_1, d_2, \delta)}{p(m, d_1, d_2, \delta)} \cdot \frac{P_{max}}{V_1} = \left(\frac{i_{rms}}{p}\right) \times \frac{P_{max}}{V_1} \tag{11}$$

As P_max/V₁ is constant and known *a priori* from specifications, minimization of I_rms is equivalent to minimization of the ratio (i_rms/p). Operation of the converter in zones I, II, and V is considered since ZVS constraints can only be satisfied in these zones. For solving the multidimensional optimization problem, m is fixed as a parameter and the optimal d₁*, d₂*, and δ* are determined, which leads to minimum (i_rms/p) for that particular m. We obtain the following optimization problem with unknown variables m, d₁, d₂, and δ:

$$\min_{\substack{d_1, d_2, \delta \in [0,1] \\ \text{ZVS}}} \frac{i_{rms}}{p}\bigg|_{m>0}(d_1, d_2, \delta) \tag{12}$$

### E. Solution for a Given m

Minimization of (12) is carried out by fixing m as a parameter and analytically solving the problem through Karush–Kuhn–Tucker conditions. The ZVS conditions are met only in zones I, II, and V, which form mutually exclusive subsets of the unit cube. The global optimum value of (i_rms/p) is found to be in zone V for all m > 0.

For m ∈ [0, 1], d₂* = 1 and the value of d₁* can be obtained by solution of:

$$(1 + m^2)^2 d_1^{*6} - 6m^2(m^2+1)d_1^{*5} + 3m^2(4m^2+1)d_1^{*4} - 2m^2(5m^2+1)d_1^{*3} + 6m^4 d_1^{*2} - m^6 = 0 \tag{13a}$$

$$\delta^* = 1 - \frac{d_1^*}{m} + \sqrt{d_1^{*2} - 2d_1^* + \frac{d_1^{*2}}{m^2}} \tag{13b}$$

For m > 1, d₁* = 1 and the value of d₂* is obtained by determining the root of:

$$(1+m^2)^2 d_2^{*7} - (2m^4+10m^2+8)d_2^{*6} + (15m^2+24)d_2^{*5} - (8m^2+34)d_2^{*4} + (4m^2+26)d_2^{*3} - 12d_2^{*2} - \frac{1}{m^2}d_2^* + \frac{2}{m^2} = 0 \tag{14a}$$

$$\delta^* = 1 - \frac{d_2^*}{m} + \sqrt{d_2^{*2} - 2d_2^* + m^2 d_2^{*2}} \tag{14b}$$

Some important observations can be made from the solution:

1. The global optimum of the problem occurs at m = 1. At this point, d₁* = 1, d₂* = 1, and δ* = 0. This means p* = 0 (or L* = 0) and i*_rms = 0. However, their ratio converges to unity. Operation at the global optimum point is thus not possible.

2. As m is increased beyond 1, the value of I*_rms × V₁/P_max slowly increases from its global optimum of 1 and then stays almost constant at 1.1.

3. For m < 1, the rms current increases rapidly as m reduces from unity. This value crosses 1.1 at m = 0.95. Thus, for achieving rms current less than or equal to 1.1 for an m < 1, m must be greater than 0.95.

Close to m = 1, p*(m) ≈ mπ/4, which implies poor controllability. For example, at m = 0.95, p*(m) = 0.175 is just 23% of the maximum power. This value reduces to zero as m = 1 is approached. So, it is not suggested to design L* for m < 1.

### F. Fixing m and Finalizing Design

Note that V₁ and f_s are fixed and known *a priori*. For a given choice of m*, the optimal value of inductance L* is obtained by evaluation of p* at m = m*. From the design analysis, rms current rises faster with change in m for m < m* when compared with m > m*. Thus, the range of m in which we should operate must always be greater than m*, which implies m* = m_min.

For any given m*, the rms current rises for m > m*. The rate of this current increase reduces with increasing m*. This implies that a higher value of m* should be chosen during design. With given converter specifications, the value of γ := m_max/m_min = V₂max/V₂min is known *a priori*. For a given value of γ and a permissible limit on the variation of rms current, the relationship between rms currents at m_max = γm* and m_min can be used to determine m*.

For example, with γ = 1.3, if we want the variation of rms current with respect to its minimum value to be less than 10%, then minimum m* = 1.3. A higher value of m* (> 1.3) is not desirable since it leads to increase of the value of the required L*.

Once m_min = m* is fixed, the turns ratio is evaluated: n = m*V₁/V₂min. From Section II-E:

$$L = L^*(m^*) = p^*(m^*) \times \frac{V_1^2}{2\pi f_s P_{max}}$$

For determining L*, p*(m) should be known. A polynomial function is fitted to determine p*(m) once m is fixed:

$$p^*(m) = -1.9m^4 + 12.6m^3 - 30.9m^2 + 34.3m - 14.07 \tag{15}$$

For operation of the converter at points different than (P_max, V₂min), the modulation strategy described in Section II-C is used [10]. For a designed n and L, the per unit power varies between p_min and p_max and m varies between m_min and m_max. Thus, any operating point lies in a rectangle on the m–p plane bounded by the points A, B, C, and D.

For P = P_max and γ = 1.3 (say), the design strategy gives m* = 1.3. Thus, p_max = p*(m = 1.3) = 0.56. V₂min corresponds to m_min = 1.3. Point A has coordinates (1.3, 0.56), m_max = 1.3 × V₂max/V₂min, and p_min = 0.56 × P_min/P_max.

### G. Component Ratings

For a converter operating in the described region, the maximum values of peak and rms currents need to be identified for switch selection. The rms current is maximum at operating point D (m_max, p_max). The peak current is also maximum at D.

**Table IV: Device, Capacitor, and Magnetics Rating**

| Component | RMS | Peak |
|-----------|-----|------|
| Switch (Pri.) | 0.84P_max/V₁ | 2.13P_max/V₁ |
| Switch (Sec.) | 0.84nP_max/V₁ | 2.13nP_max/V₁ |
| Capacitor (Pri.) Rip. RMS | 0.645P_max/V₁ | Capacitance: 0.1027P_max/(f_s V₁ ΔV₁) |
| Capacitor (Sec.) Rip. RMS | 0.702nP_max/V₁ | Capacitance: 0.112nP_max/(f_s V₁ ΔV₂) |
| Transformer A_c A_w | n: m*V₁/V₂min | I_rms: 1.19P_max/V₁ |
| | 0.641P_max/(J f_s B_m k_w) | |
| Inductor A_c A_w | I_p: 2.13P_max/V₁ | I_rms: 1.19P_max/V₁ |
| | LI_p I_rms/(J B_m k_w) | |

For designing the transformer, the core area is:

$$A_c = \frac{mV_1 d_2}{4n_s n B_m f_s}$$

where B_m is the peak flux density in core. The value of A_c is maximum when m and d₂ are maximum.

The window area is:

$$A_w = \frac{2n_s n I_{rms}}{k_w J}$$

where k_w and J are window factor and the current density, respectively.

For an external inductance added in series with the transformer, the required area product is:

$$A_c A_w = \frac{L I_{pk} I_{rms}}{J B_m k_w}$$

---

## III. Experimental Results

To validate the converter design and operation methodology, a dc–dc converter was designed with the following hardware specifications:

**Table V: Hardware Specifications**

| V₁ | V₂min | V₂max | P_min | P_max | f_s |
|----|-------|-------|-------|-------|-----|
| 400 V | 325 V | 425 V | 1 kW | 2.6 kW | 75 kHz |

The value of m* is chosen to be 1.3, which gives p* = 0.56, resulting in **n = 1.6** and **L = 73.13 μH**. With these fixed values of n, L, and the modulation strategy described in Section II-C, the maximum transformer primary rms and peak currents (at P_max and V₂max) are 7.8 A and 14.0 A, respectively. The secondary-side rms and peak currents are 12.5 A and 22.4 A, respectively.

**Component Selection:**
- SiC MOSFETs (28-A current rating) used for primary- and secondary-side switches
- Isolated gate driver (ADuM4135) for generation of gating pulses
- Primary and secondary capacitor ripple currents: 4.29 A and 7.38 A, respectively
- Film capacitors of 2.5 μF
- Transformer area product: 9.26 cm⁴
- Planar transformer (Payton): turns ratio 24:15, area product 17.5 cm⁴
- Transformer leakage inductance: 20 μH at 75 kHz
- External inductor: 53 μH (area product: 2.44 cm⁴), ferrite core (Part No: 0R45530EC)

The values of d₁* = 1, d₂* = 0.82, and δ* = 0.35 are obtained using the modulation strategy described in Section II-C.

**Table VI: Comparison at Four Operating Points of the Converter**

| Point | P (kW) | V₂ (V) | (d₁, d₂, δ) | I_rms(T) (A) | I_rms(S) (A) | I_rms(E) (A) | Zone |
|-------|--------|---------|-------------|-------------|-------------|-------------|------|
| **A** | 2.6 | 325 | (1, 0.82, 0.35) | 7.18 | 7.23 | 7.14 | V |
| **B** | 1.0 | 325 | (0.77, 0.59, 0.18) | 3.28 | 3.23 | 3.23 | I |
| **C** | 1.0 | 425 | (0.58, 0.34, 0.24) | 3.79 | 3.74 | 3.69 | I |
| **D** | 2.6 | 425 | (0.93, 0.55, 0.38) | 7.78 | 7.65 | 7.42 | I |

*T = Theoretical, S = Simulation, E = Experimental*

A close agreement between theoretical, simulation, and experimental values can be observed. For all these operating conditions, the power is less than nV₁V₂/(8f_sL), which is the maximum deliverable power.

### A. Soft Switching — Experimental Validation

For the converter operating in zone V at V₂ = V₂min and P = P_max (point A), current i₁ should be less than zero, and the currents i₂, i₃, and i₄ should be greater than zero to ensure switch to diode transition (ZVS). All the current polarities are maintained as desired, which ensures soft switching.

Switch S₂ is conducting prior to its turn-OFF (at t₀) since i_L = i₁ < 0. After t = t₀, the gate voltage v_gs,S2 starts to reduce. The gate voltage reduces below threshold implying that channel current is zero before v_ds,S2 starts to increase at t = t₁. This results in ZVS turn-OFF of S₂. At t = t₂, v_ds,S1 reduces to zero and diode D₁ starts conducting. The turn-ON of S₁ at t = t₃ happens at zero voltage indicating ZVS. Similar behavior was observed for the remaining switching transitions of the converter.

### B. Efficiency and Loss Breakup

The peak efficiency of the converter is **97%** for operation at V₂ = 325 V. The efficiency of the converter is slightly reduced for operation at maximum V₂ due to increased conduction losses.

**Theoretical loss breakdown for P_max = 2.6 kW and V₂min = 325 V (point A):**
- Primary and secondary switch rms currents: I_rms/√2 = 5.08 A and nI_rms/√2 = 8.13 A
- r_ds,on = 0.125 Ω for primary and secondary MOSFETs
- Primary conduction loss: 12.9 W
- Secondary conduction loss: 33.04 W
- Transformer and inductor resistance: r_c = 0.5 Ω at 75 kHz
- Copper conduction loss (7.18 A rms): 25.8 W
- Transformer core loss: 4.13 W (using improved Steinmetz equation, α = 1.098, β = 2.196, k_c = 0.025, p_v = 50.43 mW/cm³)
- Inductor core loss: 18.66 W (α = 0.845, β = 2.099, k_c = 0.467)
- **Total loss: 94.8 W**

Major losses are the conduction losses in the bridges and copper losses in the transformer.

---

## IV. Conclusion

In this article, a design procedure for a DAB based dc–dc converter with a given set of specifications (power range, uncontrolled port voltage range, controlled port voltage, and switching frequency) was presented. The design aimed at minimization of worst-case inductor rms current in the operating range of the converter. Modeling of the converter was carried out in the time domain, and the optimal TPS strategy was considered for minimum rms current and soft switching in the entire operating range. It was identified that the maximum rms current with optimal TPS strategy always happens at maximum power.

For the converter operating at maximum power and a given value of uncontrolled port voltage, an optimization problem was formulated for minimization of rms current with soft switching. Analytical solution of the optimization problem provided the optimal values of the design variables, i.e., transformer turns ratio and the value of the series inductance.

Further analysis showed that if the optimal design is done at the minimum value of the uncontrolled port voltage, the rms inductor current stays close to its optimal value, despite variation in the voltage. Closed-form expressions for optimal design variables obtained through curve-fitting were provided. A simple step-by-step procedure for obtaining the design parameter values from converter specifications was provided. Details of the selection of power devices, filter capacitors, and design of transformer and inductor were also given. A 2.6-kW hardware prototype was designed based on the outlined procedure. Experimental results confirmed the effectiveness of the design.

---

## Appendix A: Comparison with Literature

A comparison of computational effort of the proposed method with [24] shows that the proposed method is simple to implement, whereas the computational complexity is high in [24] for higher number of discrete points N in the range of optimization variables.

**Table VIII: Worst-Case Performance Comparison**

The proposed design method shows improvement in the worst-case rms current compared to [23] (n = 0.94, L = 78.4 μH with SPS modulation). A considerable reduction in the worst-case peak current and the output rms current is also observed.

**Table IX: Comparison of Component Sizes**

The proposed method results in reduction of magnetic component and capacitor size compared to [23].

**Table X: Loss Comparison (P = 2.6 kW and V₂ = 325 V)**

| Factor | This Paper | [23] |
|--------|-----------|------|
| Cond.–Pri. (P/V₁)² r_on,p | 2.387 | 6.996 |
| Cond.–Sec. (P/V₂min)² r_on,s | 4.034 | 4.092 |
| Copper Loss (P/V₁)² r_c | 1.194 | 3.498 |

The proposed method results in improvement of circuit performance in terms of efficiency, component size, and worst-case current stresses.

---

## Appendix B: Closed-Loop Operation

The modulation technique in [10] is used for converter operation once design parameters are fixed according to Section II-F. A closed-loop voltage controller is implemented in simulation and experiment for regulating the controlled port voltage V₁ to a given reference V₁* during disturbances. The proportional–integral controller parameters are obtained as k_p = 20 and k_i = 25 × 10³.

Dynamic performance verified for:
- Step increase in load by 10% at t = 1 ms (power settles from 2 kW to 2.4 kW)
- V₂ increased by 10% at t = 8 ms
- Experimental step change in V₁* from 360 V to 400 V (V₁ settles to 400 V)

---

## Appendix C: Discussion on Electromagnetic Compatibility

The DAB circuit along with a line impedance stabilization network is simulated to analyze the common-mode noise. According to FCC regulation, the common-mode voltage (v_cm = 0.5(v_x + v_y)) developed across 50-Ω resistance should be less than 1 mV in 150 kHz–30 MHz [27]. This regulation is violated without the EMI filter.

An EMI filter is designed to attenuate the peak (150 mV) by 150 times (43.5 dB). Accordingly, the LC filter (formed by L_cm and C_cm) should have a cutoff frequency of:

$$150 \times 10^{-\frac{43.5}{40}} = 12.24 \text{ kHz}$$

With the EMI filter, the voltage is below 1 mV conforming to the regulation.

---

## References

[1] R. De Doncker, D. Divan, and M. Kheraluwala, "A three-phase soft-switched high-power-density DC/DC converter for high-power applications," *IEEE Trans. Ind. Appl.*, vol. 27, no. 1, pp. 63–73, Jan./Feb. 1991.

[2] M. Kheraluwala, R. Gascoigne, D. Divan, and E. Baumann, "Performance characterization of a high-power dual active bridge dc-to-dc converter," *IEEE Trans. Ind. Appl.*, vol. 28, no. 6, pp. 1294–1301, Nov./Dec. 1992.

[3] A. K. Jain and R. Ayyanar, "PWM control of dual active bridge: Comprehensive analysis and experimental verification," *IEEE Trans. Power Electron.*, vol. 26, no. 4, pp. 1215–1227, Apr. 2011.

[4] H. Bai and C. Mi, "Eliminate reactive power and increase system efficiency of isolated bidirectional dual-active-bridge DC/DC converters using novel dual-phase-shift control," *IEEE Trans. Power Electron.*, vol. 23, no. 6, pp. 2905–2914, Nov. 2008.

[5] S. Wang, Z. Zheng, C. Li, K. Wang, and Y. Li, "Time domain analysis of reactive components and optimal modulation for isolated dual active bridge DC/DC converters," *IEEE Trans. Power Electron.*, vol. 34, no. 8, pp. 7143–7146, Aug. 2019.

[6] B. Zhao, Q. Song, W. Liu, G. Liu, and Y. Zhao, "Universal high-frequency-link characterization and practical fundamental-optimal strategy for dual-active-bridge DC-DC converter under PWM plus phase-shift control," *IEEE Trans. Power Electron.*, vol. 30, no. 12, pp. 6488–6494, Dec. 2015.

[7] H. Shi, H. Wen, J. Chen, Y. Hu, L. Jiang, and G. Chen, "Minimum-reactive-power scheme of dual active bridge DC-DC converter with 3-level modulated phase-shift control," *IEEE Trans. Ind. Appl.*, vol. 53, no. 6, pp. 5573–5586, Nov./Dec. 2017.

[8] F. Krismer and J. Kolar, "Closed form solution for minimum conduction loss modulation of DAB converters," *IEEE Trans. Power Electron.*, vol. 27, no. 1, pp. 174–188, Jan. 2012.

[9] S. Chakraborty and S. Chattopadhyay, "Fully ZVS, minimum RMS current operation of the dual-active half-bridge converter using closed-loop three-degree-of-freedom control," *IEEE Trans. Power Electron.*, vol. 33, no. 12, pp. 10188–10199, Dec. 2018.

[10] A. Tong, L. Hang, G. Li, X. Jiang, and S. Gao, "Modeling and analysis of dual-active-bridge isolated bidirectional DC/DC converter to minimize RMS current with whole operating range," *IEEE Trans. Power Electron.*, vol. 33, no. 6, pp. 5302–5316, Jun. 2018.

[11] B. Zhao, Q. Song, W. Liu, and W. Sun, "Current stress optimized switching strategy of isolated bidirectional DC-DC converter with dual phase shift control," *IEEE Trans. Ind. Electron.*, vol. 60, no. 10, pp. 4458–4467, Oct. 2013.

[12] N. Hou, W. Song, and M. Wu, "Minimum current stress scheme of dual active bridge DC-DC converter with unified phase shift control," *IEEE Trans. Power Electron.*, vol. 31, no. 12, pp. 8552–8561, Dec. 2016.

[13] J. Huang, Y. Wang, Z. Li, and W. Lei, "Unified triple phase shift control to minimize current stress and achieve full soft switching of isolated bidirectional DC/DC converter," *IEEE Trans. Ind. Electron.*, vol. 63, no. 7, pp. 4169–4179, Jul. 2016.

[14] Q. Gu, L. Yuan, J. Nie, J. Sun, and Z. Zhao, "Current stress minimization of dual active bridge DC-DC converter within the whole operating range," *IEEE J. Emerg. Sel. Topics Power Electron.*, vol. 7, no. 1, pp. 129–142, Mar. 2019.

[15] S. Shao, M. Jiang, W. Ye, Y. Li, J. Zhang, and K. Sheng, "Optimal phase shift control to minimize reactive power for a dual active bridge DC-DC converter," *IEEE Trans. Power Electron.*, vol. 34, no. 10, pp. 10193–10205, Oct. 2019.

[16] G. Oggier, G. O. Garcia, and A. R. Oliva, "Modulation strategy to operate the dual active bridge DC-DC converter under soft switching in the whole operating range," *IEEE Trans. Power Electron.*, vol. 26, no. 4, pp. 1228–1236, Apr. 2011.

[17] G. G. Oggier, G. O. Garcia, and A. R. Oliva, "Switching control strategy to minimize dual active bridge converter losses," *IEEE Trans. Power Electron.*, vol. 24, no. 7, pp. 1826–1838, Jul. 2009.

[18] B. Zhao, Q. Song, and W. Liu, "Efficiency characterization and optimization of isolated bidirectional DC/DC converter based on dual phase shift control for dc distribution application," *IEEE Trans. Power Electron.*, vol. 28, no. 4, pp. 1711–1727, Apr. 2013.

[19] F. Krismer and J. W. Kolar, "Efficiency optimized high current dual active bridge converter for automotive applications," *IEEE Trans. Ind. Electron.*, vol. 59, no. 7, pp. 2745–2760, Jul. 2012.

[20] U. Kundu, B. Pant, S. Sikder, A. Kumar, and P. Sensarma, "Frequency domain analysis and optimal design of isolated bidirectional series resonant converter," *IEEE Trans. Ind. Appl.*, vol. 54, no. 1, pp. 356–366, Jan./Feb. 2018.

[21] V. J. Thottuvelil, T. G. Wilson, and H. A. Owen, "Analysis and design of a push-pull current-fed converter," in *Proc. IEEE Power Electron. Spec. Conf.*, Jun. 1981, pp. 192–203.

[22] J. Biela, U. Badstuebner, and J. W. Kolar, "Design of a 5kW, 1U, 10kW/dm³ resonant DC-DC converter for telecom applications," *IEEE Trans. Power Electron.*, vol. 24, no. 7, pp. 1701–1710, Jul. 2009.

[23] C. Gammeter, F. Krismer, and J. W. Kolar, "Comprehensive conceptualization, design, and experimental verification of a weight-optimized all-SiC 2 kV/700 V DAB for an airborne wind turbine," *IEEE J. Emerg. Sel. Topics Power Electron.*, vol. 4, no. 2, pp. 638–656, Jun. 2016.

[24] V. M. Iyer, S. Gulur, and S. Bhattacharya, "Optimal design methodology for dual active bridge converter under wide voltage variation," in *Proc. IEEE Transport. Electrific. Conf. Expo.*, Jun. 2017, pp. 413–420.

[25] W. G. Hurley and W. H. Wölfle, *Transformers and Inductors for Power Electronics: Theory, Design and Applications*. New York, NY, USA: Wiley, 2013.

[26] D. Bellan, "Symmetrical-component approach for circuit modeling of EMI emissions in three-phase inverters," in *Proc. IEEE PES Asia-Pacific Power Energy Eng. Conf.*, 2019, pp. 1–5.

[27] C. R. Paul, *Introduction to Electromagnetic Compatibility*, vol. 184. New York, NY, USA: Wiley, 2006.

---

## Authors

**Dibakar Das** (Student Member, IEEE) received the B.Tech. degree from the National Institute of Technology, Durgapur, India, in 2014, and the M.S. degree in 2017 from the Indian Institute of Science, Bangalore, India, where he is currently working toward the Ph.D. degree, all in electrical engineering. His research interests include dual-active-bridge converters.

**Kaushik Basu** (Senior Member, IEEE) received the B.E. degree from the Bengal Engineering and Science University, Shibpore, India, in 2003, the M.S. degree from the Indian Institute of Science, Bangalore, India, in 2005, and the Ph.D. degree from the University of Minnesota, Minneapolis, MN, USA, in 2012, all in electrical engineering. He was a Design Engineer with Cold Watt India in 2006 and an Electronics and Control Engineer with Dynapower Corporation, Union City, CA, USA, from 2013 to 2015. He is currently an Associate Professor with the Department of Electrical Engineering, Indian Institute of Science. Dr. Basu is the Founding Chair of both IEEE Power Electronics Society's and IEEE Industrial Electronics Society's Bangalore Chapter.
