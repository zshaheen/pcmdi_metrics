def find_closest(values, bounds, targetpt):
	'''
	Given an array of values and associated bounds, find the value that is closest to a given target point.
	'''
	for j in range(len(bounds)-1):
		# print 'Is %8.3f between %8.3f and %8.3f?' % (targetpt, bounds[j], bounds[j+1])
		if bounds[j] <= targetpt and targetpt <= bounds[j+1]:
			# print 'Yes!'
			closest = values[j]
			break
	else:
		print '*** Could not find closest value! **'
		raise RuntimeError
	return closest
