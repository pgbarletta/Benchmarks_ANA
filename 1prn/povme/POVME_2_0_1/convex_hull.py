                
class ConvexHull():
    """A class to handle convex-hull calculations"""

    def get_seg_dict_num(self, seg_dict, seg_index):
        """seg_dict is a dictionary object that contains information about segments within the convex hull. The keys are 2x3 tuples, which represent two ends of a segment in space. The values of seg_dict are the number of times a segment has been part of a triangle, either 1 or 2. (Zero times would mean that the segment doesn't exist in the dictionary yet). This function looks up and returns the value of a seg_index from seg_dict
            
        Arguments:
        seg_dict -- the dictionary of segment 2x3 tuples as keys, integers as values
        seg_index -- the key of the dictionary member we are going to retrieve
        
        Returns:
        if seg_index exists in the keys of seg_dict, return the value. Otherwise, return 0
        
        """

        if seg_index[0][0] > seg_index[1][0]: # we want the index with the greater x-value, so we don't get identical segments in the dictionary more than once
            index = seg_index
        else:
            index = seg_index[::-1]
        
        if index in seg_dict:
            return seg_dict[index]
        else:
            return 0
    
    def increment_seg_dict(self, seg_dict, seg_index):
        """seg_dict is a dictionary object that contains information about segments within the convex hull. The keys are 2x3 tuples, which represent two ends of a segment in space. The values of seg_dict are the number of times a segment has been part of a triangle, either 1 or 2. (Zero times would mean that the segment doesn't exist in the dictionary yet). This function increments the values within seg_dict, or initiates them if they dont exist yet.
            
        Arguments:
        seg_dict -- the dictionary of segment 2x3 tuples as keys, integers as values
        seg_index -- the key of the dictionary member we are going to increment
        
        Returns:
        None: the values of seg_dict are received and modified by reference
        """

        if seg_index[0][0] > seg_index[1][0]: # we want the index with the greater x-value, so we don't get identical segments in the dictionary more than once
            index = seg_index
        else:
            index = seg_index[::-1]
        
        #"putting index:", index, "into seg_dict because", index[0][0], ">", index[1][0]  
        
        if index in seg_dict: # if the entry already exists in seg_dict
            seg_dict[index] += 1 # increment
        else:
            seg_dict[index] = 1 # initiate with a value of 1 because it now exists on a triangle
        return
    
    def gift_wrapping_3d(self, raw_points):
        """Gift wrapping for 3d convex hull
            
        Arguments:
        raw_points -- A nx3 array of points, where each row corresponds to an x,y,z point coordinate
        
        Returns:
        A convex hull represented by a list of triangles. Each triangle is a 3x3 array, where each row is an x,y,z coordinate in space. The 3 rows describe the location of the 3 corners of the triangle. Each of the 3 points are arranged so that a cross product will point outwards from the hull
        
        
        """

        n = numpy.shape(raw_points)[0] # number of points
        point1 = raw_points[0] # take the first point
        xaxis = numpy.array([1,0,0]) # create a ref vector pointing along x axis
        maxx = raw_points[0][0] # initiate highest x value
        points = [] # a list of tuples for easy dictionary lookup
        seg_dict = {} # a dictionary that contains the number of triangles a seg is in
        
        begintime = time.time()
        for i in range(n): # find the n with the largest x value
            point = tuple(raw_points[i])
            points.append(point)
            if point[0] > maxx:
                maxx = point[0]
                point1 = raw_points[i]
        #print "find max x:", time.time() - begintime
        
        best_dot = -1.0 # initiate dot relative to x-axis
        point2 = numpy.array(raw_points[1]) # initiate best segment
        
        # find first/best segment
        begintime = time.time()
        for i in range(n):
            pointi = raw_points[i]
            if numpy.array_equal(pointi, point1): continue
            diff_vec = pointi - point1
            diff_len = numpy.linalg.norm(diff_vec)
            
            test_dot = numpy.dot(diff_vec/diff_len,xaxis)
            if test_dot > best_dot:
                best_dot = test_dot
                point2 = pointi
        
        #print "find first segment:", time.time() - begintime
        point1 = tuple(point1)
        point2 = tuple(point2)
        ref_vec = xaxis

        # now find the best triangle
        triangles = []
        
        seg_list = set([(point1, point2),])
        norm_dict = {(point1,point2):xaxis}
        self.increment_seg_dict( seg_dict, (point1,point2) )
        
        counter = 0
        first_time = True
        
        begintime = time.time()
        section1 = 0.0
        section2 = 0.0
        section3 = 0.0
        while seg_list: # as long as there are unexplored edges of triangles in the hull...
            
            counter += 1
            seg = seg_list.pop() # take a segment out of the seg_list
            tuple1 = seg[0] # the two ends of the segment
            tuple2 = seg[1]
            point1 = numpy.array(seg[0])
            point2 = numpy.array(seg[1])
            result = self.get_seg_dict_num( seg_dict, (seg[0],seg[1]) ) 

            if result >= 2: # then we already have 2 triangles on this segment
                continue # forget about drawing a triangle for this seg

            ref_vec = norm_dict[(seg[0],seg[1])] # get the norm for a triangle that the segment is part of
            
            best_dot_cross = -1.0
            best_point = None
            
            for i in range(n): # look at each point
                
                pointi = raw_points[i]
                #if numpy.array_equal(pointi, point1) or numpy.array_equal(pointi, point2): continue # if we are trying one of the points that are point1 or point2
                diff_vec1 = point2 - point1
                #diff_len1 = numpy.linalg.norm(diff_vec1)
                diff_vec2 = pointi - point2
                #diff_len2 = numpy.linalg.norm(diff_vec2)
                
                #test_cross = numpy.cross(diff_vec1/diff_len1,diff_vec2/diff_len2)
                #test_cross = numpy.cross(diff_vec1,diff_vec2)
                test_cross = numpy.array([diff_vec1[1]*diff_vec2[2]-diff_vec1[2]*diff_vec2[1], diff_vec1[2]*diff_vec2[0]-diff_vec1[0]*diff_vec2[2], diff_vec1[0]*diff_vec2[1]-diff_vec1[1]*diff_vec2[0]]) # cross product
                
                test_cross_len = numpy.sqrt(test_cross[0]*test_cross[0] + test_cross[1]*test_cross[1] + test_cross[2]*test_cross[2]) #numpy.linalg.norm(test_cross) # get the norm of the cross product
                
                if test_cross_len <= 0.0: continue
                #test_cross_len_inv = 1 / test_cross_len
                test_cross = test_cross / test_cross_len
                dot_cross = numpy.dot(test_cross, ref_vec)
                #dot_cross = test_cross[0]*ref_vec[0] + test_cross[1]*ref_vec[1] + test_cross[2]*ref_vec[2]
                if dot_cross > best_dot_cross:
                    best_cross = test_cross
                    best_dot_cross = dot_cross
                    best_point = pointi
                    tuple3 = points[i]
                
            
            point3 = best_point
            
            if self.get_seg_dict_num( seg_dict, (tuple2,tuple1) ) > 2: continue
            if self.get_seg_dict_num( seg_dict, (tuple3,tuple2) ) > 2: continue
            if self.get_seg_dict_num( seg_dict, (tuple1,tuple3) ) > 2: continue
            
            # now we have a triangle from point1 -> point2 -> point3
            # must test each edge
            if first_time:
                self.increment_seg_dict( seg_dict, (tuple2,tuple1) )
                seg_list.add((tuple2, tuple1))
                norm_dict[(tuple2,tuple1)] = best_cross
            
            self.increment_seg_dict( seg_dict, (tuple3,tuple2) )
            seg_list.add((tuple3, tuple2))
            norm_dict[(tuple3,tuple2)] = best_cross
            
            self.increment_seg_dict( seg_dict, (tuple1,tuple3) )
            seg_list.add((tuple1, tuple3))
            norm_dict[(tuple1,tuple3)] = best_cross
            
            triangles.append((numpy.array(tuple1),numpy.array(tuple2),numpy.array(tuple3)))
            
            first_time = False
            
        #print "find all triangles:", time.time() - begintime
        
        #print "section1:", section1
        #print "section2:", section2
        #print "section3:", section3
        return triangles
    
    def akl_toussaint(self, points):
        """The Akl-Toussaint Heuristic. Given a set of points, this definition will create an octahedron whose corners are the extremes in x, y, and z directions. Every point within this octahedron will be removed because they are not part of the convex hull. This causes any expected running time for a convex hull algorithm to be reduced to linear time.
        
        Arguments:
        points -- An nx3 array of x,y,z coordinates
        
        Returns:
        All members of original set of points that fall outside the Akl-Toussaint octahedron
        
        """

        x_high = (-1e99,0,0); x_low = (1e99,0,0); y_high = (0,-1e99,0); y_low = (0,1e99,0); z_high = (0,0,-1e99); z_low = (0,0,1e99)
        
        
        for point in points: # find the corners of the octahedron
            if point[0] > x_high[0]: x_high = point
            if point[0] < x_low[0]: x_low = point
            if point[1] > y_high[1]: y_high = point
            if point[1] < y_low[1]: y_low = point
            if point[2] > z_high[2]: z_high = point
            if point[2] < z_low[2]: z_low = point
          
        octahedron = [ # define the triangles of the surfaces of the octahedron
        numpy.array((x_high,y_high,z_high)),
        numpy.array((x_high,z_low,y_high)),
        numpy.array((x_high,y_low,z_low)),
        numpy.array((x_high,z_high,y_low)),
        numpy.array((x_low,y_low,z_high)),
        numpy.array((x_low,z_low,y_low)),
        numpy.array((x_low,y_high,z_low)),
        numpy.array((x_low,z_high,y_high)),
        ]
        new_points = [] # everything outside of the octahedron
        for point in points: # now check to see if a point is inside or outside the octahedron
            outside = self.outside_hull(point, octahedron, epsilon=-1.0e-5)
            if outside:
                new_points.append(point)
            
        return numpy.array(new_points) # convert back to an array
    
    def outside_hull(self, our_point, triangles, epsilon=1.0e-5):
        """Given the hull as defined by a list of triangles, this definition will return whether a point is within these or not.
            
        Arguments:
        our_point -- an x,y,z array that is being tested to see whether it exists inside the hull or not
        triangles -- a list of triangles that define the hull
        epsilon -- needed for imprecisions in the floating-point operations.
        
        Returns:
        True if our_point exists outside of the hull, False otherwise
        
        """

        our_point = numpy.array(our_point) # convert it to an numpy.array
        for triangle in triangles:
            rel_point = our_point - triangle[0] # vector from triangle corner 0 to point
            vec1 = triangle[1] - triangle[0] # vector from triangle corner 0 to corner 1
            vec2 = triangle[2] - triangle[1] # vector from triangle corner 1 to corner 2
            our_cross = numpy.cross(vec1, vec2) # cross product between vec1 and vec2
            our_dot = numpy.dot(rel_point,our_cross) # dot product to determine whether cross is point inward or outward
            if numpy.dot(rel_point,our_cross) > epsilon: # if the dot is greater than 0, then its outside
                return True
            
        return False
