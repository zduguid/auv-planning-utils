# /usr/local/lib/python3.6
#
# - Implementation of the Approximate Convex Decomposition (ACD) algorithm
# - Link: http://masc.cs.gmu.edu/wiki/ACD
#
# Author: Zach Duguid
# Last Updated: 05/12/2018

import re
import numpy as np


# compute the Approximate Convex Decomposition (ACD) of polygon p given tolerance tau
def ACD(p, tau): 
    # get notch point with greatest concavity of polygon p
    r, point_dict = concavity(p)
    c = point_dict[r]
    
    # return p if concavity tolerance is already satisfied
    if c < tau:
        return [p]

    # resolve the notch associated with the greatest concavity 
    polygons = resolve(p, r, point_dict)

    # for each resolved polygon, recursively call ACD
    polygon_list = [] 
    for polygon in polygons:
        new_polygons = ACD(polygon, tau)
        polygon_list.extend(new_polygons)

    return polygon_list


# returns the concavity of polygon p
def concavity(p):
    # get the convex hull
    hull = convex_hull(p)
    point_dict = {}

    # initialize bride references
    left_bridge_index = -1
    right_bridge_index = 0

    # get the concavity of each point
    #   + measured by the minimum distance between the point and its corresponding bridge points
    for point in p:
        if point not in hull:
            point_dict[point] = min(get_dist(point, hull[left_bridge_index]), get_dist(point, hull[right_bridge_index]))
        else:
            point_dict[point] = 0
            left_bridge_index += 1
            right_bridge_index += 1
            if right_bridge_index == len(hull) - 1:
                right_bridge_index = 0

    # determine the maximum concavity point (notch) of the polygon
    concavity = max(point_dict.values())
    for point in p:
        if point_dict[point] == concavity:
            notch = point

    return notch, point_dict


# add an additional diagonal line such that notch r is resolved and the score function is maximized
#   + returns the two new polygons achieved by splitting p with the optimal diagonal
def resolve(p, r, point_dict):
    # constants
    Sc = 0.1
    Sd = 1.0
    best_score = 0
    best_point = None
    best_polygons = None

    # find the diagonal that yields the highest score
    for point in p:
        if point != r:
            score = (1 + Sc*point_dict[point]) / (Sd + get_dist(point,r))
            if score > best_score:
                polygons = get_resolved_polygons(p,r,point)

                # determine if notch r has been successfully resolved
                if valid_resolve(polygons, r):
                    best_polygons = get_resolved_polygons(p,r,point)
                    best_score = score
                    best_point = (point[0], point[1])

    return(best_polygons)


# return the new polygons created when diagonal between point r and point best_point is added to p 
def get_resolved_polygons(p, r, best_point):
    # get the indices of points that constitute the diagonal to be added
    for i in range(len(p)):
        if p[i] == best_point:
            index1 = i
        elif p[i] == r:
            index2 = i

    polygon1 = []
    polygon2 = []

    # derive the two resulting polygons
    for i in range(len(p)):
        if i < min(index1,index2):
            polygon1.append(p[i])
        elif i == min(index1,index2):
            polygon1.append(p[i])
            polygon2.append(p[i])
        elif i > min(index1,index2) and i < max(index1,index2):
            polygon2.append(p[i])
        elif i == max(index1,index2):
            polygon1.append(p[i])
            polygon2.append(p[i])
        elif i > max(index1,index2):
            polygon1.append(p[i])

    return polygon1,polygon2


# determine if notch r has been successfully resolved in every polygon in polygons
def valid_resolve(polygons, r):
    # if less than 3 vertices return false
    if min([len(polygon) for polygon in polygons]) < 3:
        return False

    # else assert that interior angle of notch is less than 180 degrees
    else:
        valid = True
        for polygon in polygons:

            # get the indices of the notch for the polygon 
            for i in range(len(polygon)):
                if polygon[i] == r:
                    index_r = i

            # get the indices of the pre-notch and post-notch points 
            pre_index = index_r - 1
            if index_r == len(polygon)-1:
                post_index = 0
            else:
                post_index = index_r + 1

            # determine the interior angle at the notch
            interior_angle = get_interior_angle(polygon[pre_index], polygon[index_r], polygon[post_index])

            # if interior angle is negative, this indicates greater than 180 degree interior angle
            if interior_angle < 0:
                valid = False
                break

        return valid


# get the convex hull of polygon p
def convex_hull(p):
    # initialize convex hull list
    hull_list = []
    hull_complete = False

    # add left-most point to convex hull list
    left_point_index = np.argmin([x for (x,y) in p])
    left_point = p[left_point_index]
    hull_list.append(left_point)

    # current point on the convex hull list
    previous_point = (left_point[0], left_point[1])
    heading = 0

    # iterate until the hull is complete
    while not(hull_complete):
        # constants
        current_adj = 360
        current_dist = 0

        # iterate through points to determine next to add to hull
        for next_point in p:
            if next_point != previous_point:

                # get the required adjustment angle for this point
                new_adj = get_adj_angle(heading, previous_point, next_point)

                # keep track of best candidate hull point seen so far
                if (new_adj < current_adj) or ((new_adj == current_adj) and (get_dist(previous_point, next_point) < current_dist)):
                    current_adj = new_adj
                    current_point = (next_point[0], next_point[1])
                    current_dist = get_dist(previous_point, next_point)

        # assess the hull complete condition 
        if current_point == left_point:
            hull_complete = True

        # add new point to the hull
        else:
            hull_list.append(current_point)
            heading = heading + current_adj
            previous_point = (current_point[0], current_point[1])

    return(hull_list)


# get the adjustment angle between previous point and next point
def get_adj_angle(heading, previous_point, next_point):
    # constants
    deg_in_circle = 360
    left_turn = 270
    right_turn = 90

    # calculate difference between points for each dimension
    delta_x = next_point[0] - previous_point[0]
    delta_y = next_point[1] - previous_point[1]

    # calculate the relative angle between points
    rel_angle = np.arctan2(delta_y, delta_x) * 180/np.pi

    # force rel_angle to be measured as clockwise from East
    if rel_angle < 0:
        rel_angle *= -1
    else:
        rel_angle = deg_in_circle - rel_angle

    # force rel_angle to be measured as clockwise from North
    if rel_angle < left_turn:
        rel_angle += right_turn
    else:
        rel_angle -= left_turn

    # calculate adjustment angle
    adj_angle = rel_angle - heading
    if adj_angle < 0:
        adj_angle += deg_in_circle

    return(adj_angle)


# get the interior angle found at the notch point
def get_interior_angle(prev_point, r_point, next_point):
    # constants
    deg_in_circle = 360
    left_turn = 270
    right_turn = 90

    # get heading from previous point to notch point
    heading = np.arctan2(r_point[1]-prev_point[1], r_point[0]-prev_point[0])*180/np.pi

    # force heading to be measured as clockwise from North
    if heading < 0:
        heading *= -1
    else:
        heading = deg_in_circle - heading

    # force heading to be measured as clockwise from North
    if heading < left_turn:
        heading += right_turn
    else:
        heading -= left_turn

    # calculate the interior angle
    interior_angle = 180 - get_adj_angle(heading, r_point, next_point)
    return(interior_angle)


# return the distance between previous point and next point
def get_dist(previous_point, next_point):
    return ((previous_point[0]-next_point[0])**2 + (previous_point[1]-next_point[1])**2)**0.5


# write all polygons to a text file, one polygon per line
def write_file(filename, polygons):
    out_file = open(filename, 'w+')
    for poly in polygons:
        out_file.write(str(poly) + '\n')
    out_file.close()
