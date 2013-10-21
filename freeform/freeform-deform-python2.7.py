#!/usr/bin/env python

#
# Copyright (c) 2013 by Gerald Young <supersayoyin@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import sys
import xml.etree.ElementTree as ET
import random
import pprint

from nodedict import *

def et_iter(tree, tag=None):
	if sys.hexversion >= 0x02070000:
		return tree.iter(tag)
	else:
		return iter(tree.getiterator(tag))

def adddef_usage(parent, name):
	global defs_usage
	if parent in defs_usage:
		defs_usage[parent].append(name)
	else:
		defs_usage[parent] = [name]

def xmldup_r(src):
	"Duplicate given node, respecting already exported defs"
	global defs
	global defs_usage
	dst = ET.Element(src.tag, src.attrib)
	dst.text = src.text
	if src in defs_usage:
		for def_name in defs_usage[src]:
			adddef_usage(dst, def_name)
			def_attr = defs[def_name][1][src]
			defs[def_name][1][dst] = def_attr
	for elem in src:
		dst.append(xmldup_r(elem))
	return dst

def getblinepoints(layer):
	"Find the vertex nodes of bline parameter on given layer"
	#return layer.findall('param[@name="bline"]/bline/entry/composite/point')
	params = layer.findall('param')
	for p in params:
		if 'name' in p.attrib and p.attrib['name'] == 'bline':
			return p.findall('use/bline/entry/composite/point')

def addguid(elem):
	"Add a GUID attribute to given element"
	elem.set('guid', "%032X" % random.getrandbits(128))

def parentnode(elem, root):
	"Finds parent node of specified element"
	for p in et_iter(root):
		for c in p:
			if c == elem:
				return p

def cleanemptyelem(elem):
	"Clean whitespace from element if it has no childs"
	count = 0
	for c in elem:
		count += 1
	if count == 0:
		elem.text = elem.text.strip()

def exportnew(elem, name):
	"Create new exported node from given element with given name"
	global defs
	global defs_keys
	newelem = xmldup_r(elem)
	defs[name] = (newelem, {})
	defs_keys.append(name)
	return newelem

def exportnode(elem, root, name):
	"Export specified node element to defs with given name"
	global defs
	global defs_keys
	global defs_usage
	if name in defs:
		print "exportnode: There's an exported node with name '%s' already" % name
		raise SystemExit
	parent = parentnode(elem, root)
	parent.remove(elem)
	parent.set(elem.tag, name)
	cleanemptyelem(parent)
	defs[name] = (elem[0], { parent: elem.tag })
	defs_keys.append(name)
	adddef_usage(parent, name)
	return elem

def connectnode(elem, root, name):
	"Connect exported node with specified name at location of given element"
	global defs
	global defs_usage
	if name not in defs:
		print "connectnode: Cannot find exported node with name '%s'" % name
		raise SystemExit
	parent = parentnode(elem, root)
	parent.remove(elem)
	parent.set(elem.tag, name)
	cleanemptyelem(parent)
	defs[name][1][parent] = elem.tag
	adddef_usage(parent, name)

def unexportnode(name):
	"Unexport def with specified name"
	global defs
	global defs_keys
	global defs_usage
	elem = defs[name][0]
	addguid(elem)
	uses = defs[name][1]
	for use in uses.iteritems():
		parent = use[0]
		attrib = use[1]
		defs_usage[parent].remove(name)
		del parent.attrib[attrib]
		ET.SubElement(parent, attrib).append(xmldup_r(elem))
	del defs[name]
	if name in defs_keys:
		defs_keys.remove(name)

def gendef(name, root):
	"Generate XML for def with specified name"
	global defs
	defs_section = root.find('defs')
	# Add defs section if it doesn't exist
	if defs_section == None:
		defs_section = ET.Element('defs')
		root.insert(0, defs_section)
	# Append element to defs section
	elem = defs[name][0]
	elem.set('id', name)
	defs_section.append(elem)

def paramwrap(root):
	"Wrap child element of param elements within a <use> element"
	params = root.findall('layer/param')
	for p in params:
		# Count number of childs
		count = 0
		for c in p:
			count += 1
		if count > 1:
			# param should never have more than one child
			print "paramwrap: param element with more than one child"
			raise SystemExit
		elif count == 1:
			# wrap single child inside a <use> element
			for c in p:
				child = c
			p.remove(child)
			use = ET.SubElement(p, 'use')
			use.append(child)
		elif count == 0:
			# No child elements so do nothing
			pass

def paramunwrap(root):
	"Unwrap child element of param elements within a <use> element"
	params = root.findall('layer/param')
	for p in params:
		# Count number of childs
		count = 0
		for c in p:
			count += 1
		if count > 1:
			# param should never have more than one child
			print "paramwrap: param element with more than one child"
			raise SystemExit
		elif count == 1:
			# unwrap single child inside a <use> element
			for c in p:
				use = c
			for c in use:
				child = c
			p.remove(use)
			p.append(child)
		elif count == 0:
			# No child elements so do nothing
			pass

def findparam(layer, name):
	"Find param element with specified name inside layer"
	params = layer.findall('param')
	for p in params:
		if 'name' in p.attrib and p.attrib['name'] == name:
			return p

def ntuples(lst, n):
	return zip(*[lst[i:]+lst[:i] for i in range(n)])

def ntuplesrotated(lst, n):
	return zip(*map((lambda l: l[-1:]+l[:-1]), [lst[i:]+lst[:i] for i in range(n)]))

def process(tree):
	"Process XML on given tree object"
	global defs
	global defs_keys
	global defs_usage

	defs = {}
	defs_keys = []
	defs_usage = {}
	pp = pprint.PrettyPrinter(indent=4)

	# Append new layers to canvas
	window_rectangle = xmldup_r(nodedict['layer_rectangle'])
	control_outline = xmldup_r(nodedict['layer_outline'])
	# segment01_outline = xmldup_r(nodedict['layer_outline'])
	# segment12_outline = xmldup_r(nodedict['layer_outline'])
	deformed_outline = xmldup_r(nodedict['layer_outline'])
	window_rectangle.set('desc', 'Window')
	control_outline.set('desc', 'ControlBezier')
	# segment01_outline.set('desc', 'Segment01')
	# segment12_outline.set('desc', 'Segment12')
	deformed_outline.set('desc', 'Deformed')
	tree.getroot().append(window_rectangle)
	tree.getroot().append(control_outline)
	# tree.getroot().append(segment01_outline)
	# tree.getroot().append(segment12_outline)
	tree.getroot().append(deformed_outline)

	# Wrap all child elements of all params inside a use element
	paramwrap(tree.getroot())

	# Window exports
	window_left = exportnew(nodedict['real'], 'window_left')
	window_bottom = exportnew(nodedict['real'], 'window_bottom')
	window_right = exportnew(nodedict['real'], 'window_right')
	window_top = exportnew(nodedict['real'], 'window_top')
	window_left.attrib['value'] = '%.10f' % 0.0
	window_bottom.attrib['value'] = '%.10f' % -0.5
	window_right.attrib['value'] = '%.10f' % 1.0
	window_top.attrib['value'] = '%.10f' % 0.5

	window_mid_y = exportnew(nodedict['add_real'], 'window_mid_y')
	window_mid_y.find('scalar/real').attrib['value'] = '%.10f' % 0.5
	connectnode(window_mid_y.find('lhs'), window_mid_y, 'window_bottom')
	connectnode(window_mid_y.find('rhs'), window_mid_y, 'window_top')

	window_botleft = exportnew(nodedict['composite'], 'window_botleft')
	window_topright = exportnew(nodedict['composite'], 'window_topright')
	window_midleft = exportnew(nodedict['composite'], 'window_midleft')
	window_midright = exportnew(nodedict['composite'], 'window_midright')
	connectnode(window_botleft.find('x'), window_botleft, 'window_left')
	connectnode(window_botleft.find('y'), window_botleft, 'window_bottom')
	connectnode(window_topright.find('x'), window_topright, 'window_right')
	connectnode(window_topright.find('y'), window_topright, 'window_top')
	connectnode(window_midleft.find('x'), window_midleft, 'window_left')
	connectnode(window_midleft.find('y'), window_midleft, 'window_mid_y')
	connectnode(window_midright.find('x'), window_midright, 'window_right')
	connectnode(window_midright.find('y'), window_midright, 'window_mid_y')

	window_span_x = exportnew(nodedict['substract_real'], 'window_span_x')
	connectnode(window_span_x.find('lhs'), window_span_x, 'window_right')
	connectnode(window_span_x.find('rhs'), window_span_x, 'window_left')

	window_span_x_reciprocal = exportnew(nodedict['reciprocal'], 'window_span_x_reciprocal')
	connectnode(window_span_x_reciprocal.find('link'),
			window_span_x_reciprocal, 'window_span_x')

	# Control Bezier exports
	P2 = exportnew(nodedict['vector'], 'P2')
	P1 = exportnew(nodedict['vector'], 'P1')
	P0 = exportnew(nodedict['vector'], 'P0')

	P1_minus_P0 = exportnew(nodedict['substract_vector'], 'P1_minus_P0')
	P2_minus_P1 = exportnew(nodedict['substract_vector'], 'P2_minus_P1')
	connectnode(P1_minus_P0.find('lhs'), P1_minus_P0, 'P1')
	connectnode(P1_minus_P0.find('rhs'), P1_minus_P0, 'P0')
	connectnode(P2_minus_P1.find('lhs'), P2_minus_P1, 'P2')
	connectnode(P2_minus_P1.find('rhs'), P2_minus_P1, 'P1')

	P1_minus_P0_length = exportnew(nodedict['vectorlength'], 'P1_minus_P0_length')
	P2_minus_P1_length = exportnew(nodedict['vectorlength'], 'P2_minus_P1_length')
	connectnode(P1_minus_P0_length.find('vector'), P1_minus_P0_length, 'P1_minus_P0')
	connectnode(P2_minus_P1_length.find('vector'), P2_minus_P1_length, 'P2_minus_P1')

	P1_minus_P0_length_reciprocal = exportnew(nodedict['reciprocal'],
			'P1_minus_P0_length_reciprocal')
	P2_minus_P1_length_reciprocal = exportnew(nodedict['reciprocal'],
			'P2_minus_P1_length_reciprocal')
	connectnode(P1_minus_P0_length_reciprocal.find('link'),
			P1_minus_P0_length_reciprocal, 'P1_minus_P0_length')
	connectnode(P2_minus_P1_length_reciprocal.find('link'),
			P2_minus_P1_length_reciprocal, 'P2_minus_P1_length')

	segment01_i = exportnew(nodedict['scale_vector'], 'segment01_i')
	segment12_i = exportnew(nodedict['scale_vector'], 'segment12_i')
	connectnode(segment01_i.find('link'), segment01_i, 'P1_minus_P0') 
	connectnode(segment12_i.find('link'), segment12_i, 'P2_minus_P1') 
	connectnode(segment01_i.find('scalar'), segment01_i, 'P1_minus_P0_length_reciprocal') 
	connectnode(segment12_i.find('scalar'), segment12_i, 'P2_minus_P1_length_reciprocal') 

	segment01_i_vectorx = exportnew(nodedict['vectorx'], 'segment01_i_vectorx')
	segment01_i_vectory = exportnew(nodedict['vectory'], 'segment01_i_vectory')
	segment12_i_vectorx = exportnew(nodedict['vectorx'], 'segment12_i_vectorx')
	segment12_i_vectory = exportnew(nodedict['vectory'], 'segment12_i_vectory')
	connectnode(segment01_i_vectorx.find('vector'), segment01_i_vectorx, 'segment01_i')
	connectnode(segment01_i_vectory.find('vector'), segment01_i_vectory, 'segment01_i')
	connectnode(segment12_i_vectorx.find('vector'), segment12_i_vectorx, 'segment12_i')
	connectnode(segment12_i_vectory.find('vector'), segment12_i_vectory, 'segment12_i')

	minus_segment01_i_vectory = exportnew(nodedict['substract_real'],
			'minus_segment01_i_vectory')
	minus_segment12_i_vectory = exportnew(nodedict['substract_real'],
			'minus_segment12_i_vectory')
	connectnode(minus_segment01_i_vectory.find('rhs'),
			minus_segment01_i_vectory, 'segment01_i_vectory')
	connectnode(minus_segment12_i_vectory.find('rhs'),
			minus_segment12_i_vectory, 'segment12_i_vectory')

	segment01_j = exportnew(nodedict['composite'], 'segment01_j')
	segment12_j = exportnew(nodedict['composite'], 'segment12_j')
	connectnode(segment01_j.find('x'), segment01_j, 'minus_segment01_i_vectory')
	connectnode(segment01_j.find('y'), segment01_j, 'segment01_i_vectorx')
	connectnode(segment12_j.find('x'), segment12_j, 'minus_segment12_i_vectory')
	connectnode(segment12_j.find('y'), segment12_j, 'segment12_i_vectorx')

	# Deformee exports
	firstlayer = et_iter(tree, tag='layer').next()
	pointlist = getblinepoints(firstlayer)
	pointlistenumerated = list(enumerate(pointlist))

	for p in pointlistenumerated:
		point = exportnode(p[1], tree.getroot(), 'point%04d' % p[0])

	for p in pointlistenumerated:
		point_window_translate = exportnew(nodedict['substract_vector'],
				'point%04d_window_translate' % p[0])
		connectnode(point_window_translate.find('lhs'), point_window_translate,
				'point%04d' % p[0])
		connectnode(point_window_translate.find('rhs'), point_window_translate,
				'window_midleft')

	for p in pointlistenumerated:
		point_window_translate_x = exportnew(nodedict['vectorx'],
				'point%04d_window_translate_x' % p[0])
		point_window_translate_y = exportnew(nodedict['vectory'],
				'point%04d_window_translate_y' % p[0])
		connectnode(point_window_translate_x.find('vector'), point_window_translate_x,
				'point%04d_window_translate' % p[0])
		connectnode(point_window_translate_y.find('vector'), point_window_translate_y,
				'point%04d_window_translate' % p[0])

	for p in pointlistenumerated:
		point_window_translate_x_scale = exportnew(nodedict['scale_real'],
				'point%04d_window_translate_x_scale' % p[0])
		connectnode(point_window_translate_x_scale.find('link'),
				point_window_translate_x_scale,
				'point%04d_window_translate_x' % p[0])
		connectnode(point_window_translate_x_scale.find('scalar'),
				point_window_translate_x_scale,
				'window_span_x_reciprocal')

	for p in pointlistenumerated:
		point_window = exportnew(nodedict['composite'],
				'point%04d_window' % p[0])
		connectnode(point_window.find('x'), point_window,
				'point%04d_window_translate_x_scale' % p[0])
		connectnode(point_window.find('y'), point_window,
				'point%04d_window_translate_y' % p[0])

	for p in pointlistenumerated:
		point_window_x = exportnew(nodedict['vectorx'], 'point%04d_window_x' % p[0])
		point_window_y = exportnew(nodedict['vectory'], 'point%04d_window_y' % p[0])
		connectnode(point_window_x.find('vector'), point_window_x,
				'point%04d_window' % p[0])
		connectnode(point_window_y.find('vector'), point_window_y,
				'point%04d_window' % p[0])

	# Segment01 exports
	for p in pointlistenumerated:
		segment01_point_window_x_scale = exportnew(nodedict['scale_real'],
				'segment01_point%04d_window_x_scale' % p[0])
		connectnode(segment01_point_window_x_scale.find('link'),
				segment01_point_window_x_scale,
				'point%04d_window_x' % p[0])
		connectnode(segment01_point_window_x_scale.find('scalar'),
				segment01_point_window_x_scale,
				'P1_minus_P0_length')

	for p in pointlistenumerated:
		segment01_point_i = exportnew(nodedict['scale_vector'],
				'segment01_point%04d_i' % p[0])
		connectnode(segment01_point_i.find('link'), segment01_point_i,
				'segment01_i')
		connectnode(segment01_point_i.find('scalar'), segment01_point_i,
				'segment01_point%04d_window_x_scale' % p[0])

	for p in pointlistenumerated:
		segment01_point_j = exportnew(nodedict['scale_vector'],
				'segment01_point%04d_j' % p[0])
		connectnode(segment01_point_j.find('link'), segment01_point_j,
				'segment01_j')
		connectnode(segment01_point_j.find('scalar'), segment01_point_j,
				'point%04d_window_y' % p[0])

	for p in pointlistenumerated:
		segment01_point_i_plus_j = exportnew(nodedict['add_vector'],
				'segment01_point%04d_i_plus_j' % p[0])
		connectnode(segment01_point_i_plus_j.find('lhs'), segment01_point_i_plus_j,
				'segment01_point%04d_i' % p[0])
		connectnode(segment01_point_i_plus_j.find('rhs'), segment01_point_i_plus_j,
				'segment01_point%04d_j' % p[0])

	for p in pointlistenumerated:
		segment01_point = exportnew(nodedict['add_vector'],
				'segment01_point%04d' % p[0])
		connectnode(segment01_point.find('lhs'), segment01_point, 'P0')
		connectnode(segment01_point.find('rhs'), segment01_point,
				'segment01_point%04d_i_plus_j' % p[0])

	# Segment12 exports
	for p in pointlistenumerated:
		segment12_point_window_x_scale = exportnew(nodedict['scale_real'],
				'segment12_point%04d_window_x_scale' % p[0])
		connectnode(segment12_point_window_x_scale.find('link'),
				segment12_point_window_x_scale,
				'point%04d_window_x' % p[0])
		connectnode(segment12_point_window_x_scale.find('scalar'),
				segment12_point_window_x_scale,
				'P2_minus_P1_length')

	for p in pointlistenumerated:
		segment12_point_i = exportnew(nodedict['scale_vector'],
				'segment12_point%04d_i' % p[0])
		connectnode(segment12_point_i.find('link'), segment12_point_i,
				'segment12_i')
		connectnode(segment12_point_i.find('scalar'), segment12_point_i,
				'segment12_point%04d_window_x_scale' % p[0])

	for p in pointlistenumerated:
		segment12_point_j = exportnew(nodedict['scale_vector'],
				'segment12_point%04d_j' % p[0])
		connectnode(segment12_point_j.find('link'), segment12_point_j,
				'segment12_j')
		connectnode(segment12_point_j.find('scalar'), segment12_point_j,
				'point%04d_window_y' % p[0])

	for p in pointlistenumerated:
		segment12_point_i_plus_j = exportnew(nodedict['add_vector'],
				'segment12_point%04d_i_plus_j' % p[0])
		connectnode(segment12_point_i_plus_j.find('lhs'), segment12_point_i_plus_j,
				'segment12_point%04d_i' % p[0])
		connectnode(segment12_point_i_plus_j.find('rhs'), segment12_point_i_plus_j,
				'segment12_point%04d_j' % p[0])

	for p in pointlistenumerated:
		segment12_point = exportnew(nodedict['add_vector'],
				'segment12_point%04d' % p[0])
		connectnode(segment12_point.find('lhs'), segment12_point, 'P1')
		connectnode(segment12_point.find('rhs'), segment12_point,
				'segment12_point%04d_i_plus_j' % p[0])

	# Deformed curve exports
	pointtuples = ntuples(pointlistenumerated, 2)

	for ptuple in pointtuples:
		segment01_midpoint = exportnew(nodedict['add_vector'],
				'segment01_midpoint%04d' % ptuple[0][0])
		connectnode(segment01_midpoint.find('lhs'), segment01_midpoint,
				'segment01_point%04d' % ptuple[0][0])
		connectnode(segment01_midpoint.find('rhs'), segment01_midpoint,
				'segment01_point%04d' % ptuple[1][0])
		segment01_midpoint.find('scalar/real').set('value', '%.10f' % 0.5)

	for ptuple in pointtuples:
		segment12_midpoint = exportnew(nodedict['add_vector'],
				'segment12_midpoint%04d' % ptuple[0][0])
		connectnode(segment12_midpoint.find('lhs'), segment12_midpoint,
				'segment12_point%04d' % ptuple[0][0])
		connectnode(segment12_midpoint.find('rhs'), segment12_midpoint,
				'segment12_point%04d' % ptuple[1][0])
		segment12_midpoint.find('scalar/real').set('value', '%.10f' % 0.5)

	# Curve t parameter exports
	for ptuple in pointtuples:
		curve_t_start = exportnew(nodedict['reference_real'],
				'curve%04d_t_start' % ptuple[0][0])
		connectnode(curve_t_start.find('link'), curve_t_start,
				'point%04d_window_x' % ptuple[0][0])

	for ptuple in pointtuples:
		curve_one_minus_t_start = exportnew(nodedict['substract_real'],
				'curve%04d_one_minus_t_start' % ptuple[0][0])
		connectnode(curve_one_minus_t_start.find('rhs'), curve_one_minus_t_start,
				'curve%04d_t_start' % ptuple[0][0])
		curve_one_minus_t_start.find('lhs/real').set('value', '%.10f' % 1.0)

	for ptuple in pointtuples:
		curve_t_end = exportnew(nodedict['reference_real'],
				'curve%04d_t_end' % ptuple[0][0])
		connectnode(curve_t_end.find('link'), curve_t_end,
				'point%04d_window_x' % ptuple[1][0])

	for ptuple in pointtuples:
		curve_one_minus_t_end = exportnew(nodedict['substract_real'],
				'curve%04d_one_minus_t_end' % ptuple[0][0])
		connectnode(curve_one_minus_t_end.find('rhs'), curve_one_minus_t_end,
				'curve%04d_t_end' % ptuple[0][0])
		curve_one_minus_t_end.find('lhs/real').set('value', '%.10f' % 1.0)

	for ptuple in pointtuples:
		curve_t_mid = exportnew(nodedict['add_real'],
				'curve%04d_t_mid' % ptuple[0][0])
		connectnode(curve_t_mid.find('lhs'), curve_t_mid,
				'point%04d_window_x' % ptuple[0][0])
		connectnode(curve_t_mid.find('rhs'), curve_t_mid,
				'point%04d_window_x' % ptuple[1][0])
		curve_t_mid.find('scalar/real').set('value', '%.10f' % 0.5)

	for ptuple in pointtuples:
		curve_one_minus_t_mid = exportnew(nodedict['substract_real'],
				'curve%04d_one_minus_t_mid' % ptuple[0][0])
		connectnode(curve_one_minus_t_mid.find('rhs'), curve_one_minus_t_mid,
				'curve%04d_t_mid' % ptuple[0][0])
		curve_one_minus_t_mid.find('lhs/real').set('value', '%.10f' % 1.0)

	# Curve startpoint exports
	for ptuple in pointtuples:
		curve_startpoint_lhs = exportnew(nodedict['scale_vector'],
				'curve%04d_startpoint_lhs' % ptuple[0][0])
		connectnode(curve_startpoint_lhs.find('link'), curve_startpoint_lhs,
				'segment01_point%04d' % ptuple[0][0])
		connectnode(curve_startpoint_lhs.find('scalar'), curve_startpoint_lhs,
				'curve%04d_one_minus_t_start' % ptuple[0][0])

	for ptuple in pointtuples:
		curve_startpoint_rhs = exportnew(nodedict['scale_vector'],
				'curve%04d_startpoint_rhs' % ptuple[0][0])
		connectnode(curve_startpoint_rhs.find('link'), curve_startpoint_rhs,
				'segment12_point%04d' % ptuple[0][0])
		connectnode(curve_startpoint_rhs.find('scalar'), curve_startpoint_rhs,
				'curve%04d_t_start' % ptuple[0][0])

	for ptuple in pointtuples:
		curve_startpoint = exportnew(nodedict['add_vector'],
				'curve%04d_startpoint' % ptuple[0][0])
		connectnode(curve_startpoint.find('lhs'), curve_startpoint,
				'curve%04d_startpoint_lhs' % ptuple[0][0])
		connectnode(curve_startpoint.find('rhs'), curve_startpoint,
				'curve%04d_startpoint_rhs' % ptuple[0][0])

	# Curve endpoint exports
	for ptuple in pointtuples:
		curve_endpoint_lhs = exportnew(nodedict['scale_vector'],
				'curve%04d_endpoint_lhs' % ptuple[0][0])
		connectnode(curve_endpoint_lhs.find('link'), curve_endpoint_lhs,
				'segment01_point%04d' % ptuple[1][0])
		connectnode(curve_endpoint_lhs.find('scalar'), curve_endpoint_lhs,
				'curve%04d_one_minus_t_end' % ptuple[0][0])

	for ptuple in pointtuples:
		curve_endpoint_rhs = exportnew(nodedict['scale_vector'],
				'curve%04d_endpoint_rhs' % ptuple[0][0])
		connectnode(curve_endpoint_rhs.find('link'), curve_endpoint_rhs,
				'segment12_point%04d' % ptuple[1][0])
		connectnode(curve_endpoint_rhs.find('scalar'), curve_endpoint_rhs,
				'curve%04d_t_end' % ptuple[0][0])

	for ptuple in pointtuples:
		curve_endpoint = exportnew(nodedict['add_vector'],
				'curve%04d_endpoint' % ptuple[0][0])
		connectnode(curve_endpoint.find('lhs'), curve_endpoint,
				'curve%04d_endpoint_lhs' % ptuple[0][0])
		connectnode(curve_endpoint.find('rhs'), curve_endpoint,
				'curve%04d_endpoint_rhs' % ptuple[0][0])

	# Curve midpoint exports
	for ptuple in pointtuples:
		curve_midpoint_lhs = exportnew(nodedict['scale_vector'],
				'curve%04d_midpoint_lhs' % ptuple[0][0])
		connectnode(curve_midpoint_lhs.find('link'), curve_midpoint_lhs,
				'segment01_midpoint%04d' % ptuple[0][0])
		connectnode(curve_midpoint_lhs.find('scalar'), curve_midpoint_lhs,
				'curve%04d_one_minus_t_mid' % ptuple[0][0])

	for ptuple in pointtuples:
		curve_midpoint_rhs = exportnew(nodedict['scale_vector'],
				'curve%04d_midpoint_rhs' % ptuple[0][0])
		connectnode(curve_midpoint_rhs.find('link'), curve_midpoint_rhs,
				'segment12_midpoint%04d' % ptuple[0][0])
		connectnode(curve_midpoint_rhs.find('scalar'), curve_midpoint_rhs,
				'curve%04d_t_mid' % ptuple[0][0])

	for ptuple in pointtuples:
		curve_midpoint = exportnew(nodedict['add_vector'],
				'curve%04d_midpoint' % ptuple[0][0])
		connectnode(curve_midpoint.find('lhs'), curve_midpoint,
				'curve%04d_midpoint_lhs' % ptuple[0][0])
		connectnode(curve_midpoint.find('rhs'), curve_midpoint,
				'curve%04d_midpoint_rhs' % ptuple[0][0])

	# Curve controlpoint exports
	for ptuple in pointtuples:
		curve_controlpoint_lhs = exportnew(nodedict['scale_vector'],
				'curve%04d_controlpoint_lhs' % ptuple[0][0])
		connectnode(curve_controlpoint_lhs.find('link'), curve_controlpoint_lhs,
				'curve%04d_midpoint' % ptuple[0][0])
		curve_controlpoint_lhs.find('scalar/real').set('value', '%.10f' % 4.0)

	for ptuple in pointtuples:
		curve_controlpoint_rhs = exportnew(nodedict['add_vector'],
				'curve%04d_controlpoint_rhs' % ptuple[0][0])
		connectnode(curve_controlpoint_rhs.find('lhs'), curve_controlpoint_rhs,
				'curve%04d_startpoint' % ptuple[0][0])
		connectnode(curve_controlpoint_rhs.find('rhs'), curve_controlpoint_rhs,
				'curve%04d_endpoint' % ptuple[0][0])

	for ptuple in pointtuples:
		curve_controlpoint = exportnew(nodedict['substract_vector'],
				'curve%04d_controlpoint' % ptuple[0][0])
		connectnode(curve_controlpoint.find('lhs'), curve_controlpoint,
				'curve%04d_controlpoint_lhs' % ptuple[0][0])
		connectnode(curve_controlpoint.find('rhs'), curve_controlpoint,
				'curve%04d_controlpoint_rhs' % ptuple[0][0])
		curve_controlpoint.find('scalar/real').set('value', '%.10f' % 0.5)

	# Tangent exports
	pointtuplesrotate = ntuplesrotated(pointlistenumerated, 2)

	for ptuple in pointtuplesrotate:
		curve_tangent1 = exportnew(nodedict['substract_vector'],
				'curve%04d_tangent1' % ptuple[1][0])
		connectnode(curve_tangent1.find('lhs'), curve_tangent1,
				'curve%04d_startpoint' % ptuple[1][0])
		connectnode(curve_tangent1.find('rhs'), curve_tangent1,
				'curve%04d_controlpoint' % ptuple[0][0])
		curve_tangent1.find('scalar/real').set('value', '%.10f' % 2.0)
		curve_tangent2 = exportnew(nodedict['substract_vector'],
				'curve%04d_tangent2' % ptuple[1][0])
		connectnode(curve_tangent2.find('lhs'), curve_tangent2,
				'curve%04d_controlpoint' % ptuple[1][0])
		connectnode(curve_tangent2.find('rhs'), curve_tangent2,
				'curve%04d_startpoint' % ptuple[1][0])
		curve_tangent2.find('scalar/real').set('value', '%.10f' % 2.0)

	# Connect to layers
	window_rectangle_point1 = findparam(window_rectangle, 'point1')
	window_rectangle_point2 = findparam(window_rectangle, 'point2')
	connectnode(window_rectangle_point1.find('use'), window_rectangle, 'window_botleft')
	connectnode(window_rectangle_point2.find('use'), window_rectangle, 'window_topright')

	control_outline_bline = findparam(control_outline, 'bline').find('use/bline')
	control_outline_bline.set('loop', 'false')
	control_outline_entry = control_outline_bline.find('entry')
	connectnode(control_outline_entry.find('composite/point'),
			control_outline_entry, 'P0')
	control_outline_entry = xmldup_r(nodedict['bline_entry'])
	connectnode(control_outline_entry.find('composite/point'),
			control_outline_entry, 'P1')
	control_outline_bline.append(control_outline_entry)
	control_outline_entry = xmldup_r(nodedict['bline_entry'])
	connectnode(control_outline_entry.find('composite/point'),
			control_outline_entry, 'P2')
	control_outline_bline.append(control_outline_entry)

	# segment01_outline_bline = findparam(segment01_outline, 'bline').find('use/bline')
	# segment12_outline_bline = findparam(segment12_outline, 'bline').find('use/bline')
	# segment01_outline_bline.remove(segment01_outline_bline.find('entry'))
	# segment12_outline_bline.remove(segment12_outline_bline.find('entry'))

	# for p in enumerate(pointlist):
		# segment01_entry = xmldup_r(nodedict['bline_entry'])
		# segment12_entry = xmldup_r(nodedict['bline_entry'])
		# connectnode(segment01_entry.find('composite/point'), segment01_entry, 
				# 'segment01_point%04d' % p[0])
		# connectnode(segment12_entry.find('composite/point'), segment12_entry, 
				# 'segment12_point%04d' % p[0])
		# segment01_outline_bline.append(segment01_entry)
		# segment12_outline_bline.append(segment12_entry)

	deformed_outline_bline = findparam(deformed_outline, 'bline').find('use/bline')
	deformed_outline_bline.remove(deformed_outline_bline.find('entry'))

	for p in enumerate(pointlist):
		deformed_entry = xmldup_r(nodedict['bline_entry'])
		connectnode(deformed_entry.find('composite/point'), deformed_entry, 
				'curve%04d_startpoint' % p[0])
		connectnode(deformed_entry.find('composite/t1'), deformed_entry, 
				'curve%04d_tangent1' % p[0])
		connectnode(deformed_entry.find('composite/t2'), deformed_entry, 
				'curve%04d_tangent2' % p[0])
		deformed_outline_bline.append(deformed_entry)
		deformed_entry.find('composite/split/bool').set('value', 'true')

	# Unexport all exported values
	for k in list(defs_keys):
		unexportnode(k)

	# Generate defs section
	for k in defs_keys:
		gendef(k, tree.getroot())

	# Unwrap all child elements of all params inside a use element
	paramunwrap(tree.getroot())

if __name__ == "__main__":
	# Open source SIF file
	if len(sys.argv) < 2:
		print "Not enough arguments"
		raise SystemExit
	else:
		try:
			f = open(sys.argv[1])
		except IOError:
			print "Could not open file:", sys.argv[1]
			raise SystemExit

	# Parse into ElementTree
	tree = ET.parse(f)
	f.close()

	# Main processing
	process(tree)

	# Open output file
	try:
		f = open(sys.argv[1], 'w')
	except IOError:
		print "Could not open output file:", sys.argv[1]
		raise SystemExit

	tree.write(f)

