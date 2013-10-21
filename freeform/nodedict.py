#!/usr/bin/env python

#
# Copyright (c) 2013 by Gerald Young <supersayoyin@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import textwrap
import xml.etree.ElementTree as ET

nodedict = {
		'real': ET.XML('<real value="0.0000000000" />'),
		'vector': ET.XML(textwrap.dedent('''
			<vector>
			  <x>0.0000000000</x>
			  <y>0.0000000000</y>
			</vector>
			''')),
		'add_real': ET.XML(textwrap.dedent('''
			<add type="real">
			  <lhs>
			    <vector>
			      <x>0.0000000000</x>
			      <y>0.0000000000</y>
			    </vector>
			  </lhs>
			  <rhs>
			    <vector>
			      <x>0.0000000000</x>
			      <y>0.0000000000</y>
			    </vector>
			  </rhs>
			  <scalar>
			    <real value="1.0000000000"/>
			  </scalar>
			</add>
			''')),
		'add_vector': ET.XML(textwrap.dedent('''
			<add type="vector">
			  <lhs>
			    <vector>
			      <x>0.0000000000</x>
			      <y>0.0000000000</y>
			    </vector>
			  </lhs>
			  <rhs>
			    <vector>
			      <x>0.0000000000</x>
			      <y>0.0000000000</y>
			    </vector>
			  </rhs>
			  <scalar>
			    <real value="1.0000000000"/>
			  </scalar>
			</add>
			''')),
		'composite': ET.XML(textwrap.dedent('''
			<composite type="vector">
			  <x>
			    <real value="0.0000000000"/>
			    </x>
			  <y>
			    <real value="0.0000000000"/>
			  </y>
			</composite>
			''')),
		'substract_real': ET.XML(textwrap.dedent('''
			<subtract type="real">
			  <lhs>
			    <real value="0.0000000000"/>
			  </lhs>
			  <rhs>
			    <real value="0.0000000000"/>
			  </rhs>
			  <scalar>
			    <real value="1.0000000000"/>
			  </scalar>
			</subtract>
			''')),
		'substract_vector': ET.XML(textwrap.dedent('''
			<subtract type="vector">
			  <lhs>
			    <vector>
			      <x>0.0000000000</x>
			      <y>0.0000000000</y>
			    </vector>
			  </lhs>
			  <rhs>
			    <vector>
			      <x>0.0000000000</x>
			      <y>0.0000000000</y>
			    </vector>
			  </rhs>
			  <scalar>
			    <real value="1.0000000000"/>
			  </scalar>
			</subtract>
			''')),
		'reciprocal': ET.XML(textwrap.dedent('''
			<reciprocal type="real">
			  <link>
			    <real value="0.0000000000"/>
			  </link>
			  <epsilon>
			    <real value="0.0000010000"/>
			  </epsilon>
			  <infinite>
			    <real value="999999.0000000000"/>
			  </infinite>
			</reciprocal>
			''')),
		'vectorlength': ET.XML(textwrap.dedent('''
			<vectorlength type="real">
			  <vector>
			    <vector>
			      <x>0.0000000000</x>
			      <y>0.0000000000</y>
			    </vector>
			  </vector>
			</vectorlength>
			''')),
		'scale_real': ET.XML(textwrap.dedent('''
			<scale type="real">
			  <link>
			    <real value="0.0000000000"/>
			  </link>
			  <scalar>
			    <real value="1.0000000000"/>
			  </scalar>
			</scale>
			''')),
		'scale_vector': ET.XML(textwrap.dedent('''
			<scale type="vector">
			  <link>
			    <vector>
			      <x>0.0000000000</x>
			      <y>0.0000000000</y>
			    </vector>
			  </link>
			  <scalar>
			    <real value="1.0000000000"/>
			  </scalar>
			</scale>
			''')),
		'vectorx': ET.XML(textwrap.dedent('''
			<vectorx type="real">
			  <vector>
			    <vector>
			      <x>0.0000000000</x>
			      <y>0.0000000000</y>
			    </vector>
			  </vector>
			</vectorx>
			''')),
		'vectory': ET.XML(textwrap.dedent('''
			<vectory type="real">
			  <vector>
			    <vector>
			      <x>0.0000000000</x>
			      <y>0.2500000000</y>
			    </vector>
			  </vector>
			</vectory>
			''')),
		'layer_outline': ET.XML(textwrap.dedent('''
			<layer type="outline" active="true" version="0.2" desc="NewSpline Outline">
			  <param name="z_depth">
			    <real value="0.0000000000"/>
			  </param>
			  <param name="amount">
			    <real value="1.0000000000"/>
			  </param>
			  <param name="blend_method">
			    <integer value="0"/>
			  </param>
			  <param name="color">
			    <color>
			      <r>0.000000</r>
			      <g>0.000000</g>
			      <b>0.000000</b>
			      <a>1.000000</a>
			    </color>
			  </param>
			  <param name="origin">
			    <vector>
			      <x>0.0000000000</x>
			      <y>0.0000000000</y>
			    </vector>
			  </param>
			  <param name="invert">
			    <bool value="false"/>
			  </param>
			  <param name="antialias">
			    <bool value="true"/>
			  </param>
			  <param name="feather">
			    <real value="0.0000000000"/>
			  </param>
			  <param name="blurtype">
			    <integer value="1"/>
			  </param>
			  <param name="winding_style">
			    <integer value="0"/>
			  </param>
			  <param name="bline">
			    <bline type="bline_point" loop="true">
			      <entry>
			        <composite type="bline_point">
			          <point>
			            <vector>
			              <x>0.0000000000</x>
			              <y>0.0000000000</y>
			            </vector>
			          </point>
			          <width>
			            <real value="1.0000000000"/>
			          </width>
			          <origin>
			            <real value="0.5000000000"/>
			          </origin>
			          <split>
			            <bool value="false"/>
			          </split>
			          <t1>
			            <radial_composite type="vector">
			              <radius>
			                <real value="0.0000000000"/>
			              </radius>
			              <theta>
			                <angle value="0.000000"/>
			              </theta>
			            </radial_composite>
			          </t1>
			          <t2>
			            <radial_composite type="vector">
			              <radius>
			                <real value="0.0000000000"/>
			              </radius>
			              <theta>
			                <angle value="0.000000"/>
			              </theta>
			            </radial_composite>
			          </t2>
			        </composite>
			      </entry>
			    </bline>
			  </param>
			  <param name="width">
			    <real value="0.0500000000"/>
			  </param>
			  <param name="expand">
			    <real value="0.0000000000"/>
			  </param>
			  <param name="sharp_cusps">
			    <bool value="true"/>
			  </param>
			  <param name="round_tip[0]">
			    <bool value="true"/>
			  </param>
			  <param name="round_tip[1]">
			    <bool value="true"/>
			  </param>
			  <param name="loopyness">
			    <real value="1.0000000000"/>
			  </param>
			  <param name="homogeneous_width">
			    <bool value="true"/>
			  </param>
			</layer>
			''')),
		'layer_rectangle': ET.XML(textwrap.dedent('''
			<layer type="rectangle" active="true" version="0.2" desc="Rectangle005">
			  <param name="z_depth">
			    <real value="0.0000000000"/>
			  </param>
			  <param name="amount">
			    <real value="1.0000000000"/>
			  </param>
			  <param name="blend_method">
			    <integer value="0"/>
			  </param>
			  <param name="color">
			    <color>
			      <r>0.000000</r>
			      <g>0.000000</g>
			      <b>0.000000</b>
			      <a>0.500000</a>
			    </color>
			  </param>
			  <param name="point1">
			    <vector>
			      <x>0.0000000000</x>
			      <y>0.0000000000</y>
			    </vector>
			  </param>
			  <param name="point2">
			    <vector>
			      <x>0.0000000000</x>
			      <y>0.0000000000</y>
			    </vector>
			  </param>
			  <param name="expand">
			    <real value="0.0000000000"/>
			  </param>
			  <param name="invert">
			    <bool value="false"/>
			  </param>
			</layer>
			''')),
		'bline_entry': ET.XML(textwrap.dedent('''
			<entry>
			  <composite type="bline_point">
			    <point>
			      <vector>
			        <x>0.0000000000</x>
			        <y>0.0000000000</y>
			      </vector>
			    </point>
			    <width>
			      <real value="1.0000000000"/>
			    </width>
			    <origin>
			      <real value="0.5000000000"/>
			    </origin>
			    <split>
			      <bool value="false"/>
			    </split>
			    <t1>
			      <radial_composite type="vector">
			        <radius>
			          <real value="0.0000000000"/>
			        </radius>
			        <theta>
			          <angle value="0.000000"/>
			        </theta>
			      </radial_composite>
			    </t1>
			    <t2>
			      <radial_composite type="vector">
			        <radius>
			          <real value="0.0000000000"/>
			        </radius>
			        <theta>
			          <angle value="0.000000"/>
			        </theta>
			      </radial_composite>
			    </t2>
			  </composite>
			</entry>
			''')),
		'reference_real': ET.XML(textwrap.dedent('''
			<reference type="real">
			  <link>
			    <real value="0.0000000000" />
			  </link>
			</reference>
			''')),
		'reference_vector': ET.XML(textwrap.dedent('''
			<reference type="vector">
			  <link>
			    <vector>
			      <x>0.0000000000</x>
			      <y>0.0000000000</y>
			    </vector>
			  </link>
			</reference>
			''')),
		}
