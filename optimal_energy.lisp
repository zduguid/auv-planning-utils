(defun energy-exp (x0 y0 xf yf u v sensor-on)
	;; Data from Slocum Glider masterdata file:
	;; 	+ sensor: f_speed_min(m/s) 0.05	#in, minimum allowable speed input. 
	;; 	+ sensor: u_max_thruster_speed(m/s) 1.5 # Max estimated thruster speed.
	;; Nomenclature:
	;; 	+ v-g = velocity of glider thruster engine
	;; 	+ v-c = velocity of ocean currents
	;; 	+ v-t = total velocity, v-g + v-c

	;; contstants that define relationship between thruster speed and input motor current
	(let* (
		;; contstants that define relationship between thruster speed and input motor current
		(c0 0.1473)
		(c1 0.908)
		(c2 -0.2083)

		;; define the number of linearily spaced samples to consider when optimizing glider speed
		(num-sample 100)

		;; hotel load information for when sensor is on and when sensor is off, [Amps]
		(hotel (if sensor-on 0.5 0.25))

		;; buoyancy engine power draw, [Amps]
		;;	+ assumes that buoyancy engine makes negligible contribution to glider ground speed
		(buoyancy-engine 0.5)

		;; magnitude of ocean currents, [m/s]
		(v-c (mag u v))	

		;; temp variable used to correct for numerical error that arises when taking acos 
		(temp (if (= v-c 0) nil (/ (dot-product (- xf x0) (- yf y0) u v) (* (mag (- xf x0) (- yf y0)) v-c))))

		;; angle between travel vector and ocean current vector, [rad]
		(theta (if (= v-c 0) nil (get-theta temp)))

		;; angle between travel vector and positive x-axis, [rad]
		(phi (get-heading x0 y0 xf yf))

		;; the perpendicular component of the ocean currents relative to direction of motion, [m/s]
		(v-c-perp (if (= v-c 0) 0 (* v-c (sin theta))))

		;; the parallel component of the ocean currents relative to direction of motion, [m/s]
		(v-c-para (if (= v-c 0) 0 (* v-c (cos theta))))

		;; minimum and maxmim speed that glider can achieve, along with the corresponding input current values
		(v-min (max (if (< v-c-para 0) (mag v-c-perp v-c-para) v-c-perp) 0.05))
		(v-max 1.0)
		(i-min nil)
		(i-max nil)
		(opt-objective nil)
		(opt-i nil)
		(opt-v nil)
		(opt-v-x nil)
		(opt-v-y nil)
		(loc-v-x nil)
		(loc-v-y nil)
		)

	;; if v-min > v-max, impossible to make this transition
	(if (> v-min v-max) (return (error "Impossible to reach")))

	;; else, loop through viable current inputs to determine the most energy optimal path
	(setf i-min (get-i v-min c0 c1 c2))
	(setf i-max (get-i v-max c0 c1 c2))

	;; calculate the energy optimal input current that should be used in the given scenario
	(loop for i from (+ i-min (/ (- i-max i-min) num-sample)) to i-max by (/ (- i-max i-min) num-sample) do
		(if (or (not opt-objective) (< (objective i hotel buoyancy-engine v-c-para v-c-perp c0 c1 c2) opt-objective))
			(progn
				(setf opt-objective (objective i hotel buoyancy-engine v-c-para v-c-perp c0 c1 c2))
				(setf opt-i i))))

	;; calulate the optimal velocity using opt-i
	(setf opt-v (get-v opt-i c0 c1 c2))

	;; convert the energy loss from [A*s/m] to [A*hrs/km]
	(setf opt-objective (* 1000 (/ 1 60) (/ 1 60) opt-objective))

	;; determine the glider velocity in local glider coordinates, [m/s]
	(if (= (cross-product (- xf x0) (- yf y0) u v) 0)
		(progn
			(setf loc-v-x opt-v)
			(setf loc-v-y 0))
		(if (< (cross-product (- xf x0) (- yf y0) u v) 0)
			(progn
				(setf loc-v-x (expt (- (expt opt-v 2) (expt v-c-perp 2)) 0.5))
				(setf loc-v-y v-c-perp))
			(progn 
				(setf loc-v-x (expt (- (expt opt-v 2) (expt v-c-perp 2)) 0.5))
				(setf loc-v-y (* -1 v-c-perp)))))

	;; determine glider velocity in global x,y coordinates, [m/s]
	(setf opt-v-x (+ (* (cos phi) loc-v-x) (* -1 (sin phi) loc-v-y)))
	(setf opt-v-y (+ (* (sin phi) loc-v-x) (*    (cos phi) loc-v-y)))

	;; helpful print statement for when performing unit testing
	(printem "optimal  velocity:    " opt-v "[m/s]") (format t "~%")
	(printem "optimal  energy loss: " opt-objective "[A*hrs/km]") (format t "~%")
	(printem "local    x-velocity:  " loc-v-x "[m/s]") (format t "~%")
	(printem "local    y-velocity:  " loc-v-y "[m/s]") (format t "~%")
	(printem "inertial x-velocity:  " opt-v-x "[m/s]") (format t "~%")
	(printem "inertial y-velocity:  " opt-v-y "[m/s]")

	;; return the energy loss, [A*hrs/km]  
	; (return opt-objective)

	;; return the glider velocity, [m/s]
	; (return (list opt-v-x opt-v-y))
	)
)


;; determines angle theta between distance vector and ocean currents vector
;;	+ asserts that acos does not 
(defun get-theta (temp)
	(if (< temp -1) pi 
		(if (> temp 1) 0 (acos temp))))


;; return the dot-product between two vectors
(defun dot-product (x0 y0 x1 y1)
	(+ (* x0 x1) (* y0 y1)))


;; return the cross-product between two vectors 
(defun cross-product (x0 y0 x1 y1)
	(- (* x0 y1) (* y0 x1)))


;; return the magnitude of the vector
(defun mag (x y)
	(expt (+ (expt x 2) (expt y 2)) 0.5))


;; determines angle theta between distance vector and ocean currents vector
;;	+ asserts that acos does not return complex valued numbers due to numerical errors
(defun get-theta (temp)
	(if (< temp -1) pi 
		(if (> temp 1) 0 (acos temp))))


;; given a target velocity and the thruster speed-power coefficients, return the necessary input current
(defun get-i (v-target c0 c1 c2)
	(max (/ (+ (* -1 c1) (expt (+ (expt c1 2) (* -4 c0 c2) (* 4 c2 v-target)) 0.5)) (* 2 c2)) 0))


;; given an input current and the thruster speed-power coefficients, return the glider speed
(defun get-v (i c0 c1 c2)
	(+ c0 (* c1 i) (* c2 (expt i 2))))


;; evaluate the energy expenditure necessary to complete a path given the scenario
(defun objective (i hotel buoyancy-engine v-c-para v-c-perp c0 c1 c2)
	(/ (+ hotel buoyancy-engine i) (+ v-c-para (expt (- (expt (get-v i c0 c1 c2) 2) (expt v-c-perp 2)) 0.5))))


;; given the current position and final position, returns the heading relative to the postive x-axis, [rad]
;; 	+ assert that angle is positive so that a clock-wise coordinate transformation can be applied
(defun get-heading (x0 y0 x1 y1)
	(if (< (atan (- y1 y0) (- x1 x0)) 0) (+ (* 2 pi) (atan (- y1 y0) (- x1 x0))) (atan (- y1 y0) (- x1 x0))))


;; calculate the glider velocity vectors required to achieve an energy optimality transition in this scenario
(defun get-glider-velocity (opt-v v-c-perp))


;; helper function for printing unit test results
(defun printem (&rest args)
  (format t "~{~a~^ ~}" args))


;; unit tests 
(defun test ()
	(format t "~%~%>> zero currents, sensors off: ~%")
	(energy-exp 0 0 1 1 0 0 nil)

	(format t "~%~%>> zero currents, sensors on: ~%")
	(energy-exp 0 0 1 1 0 0 t)

	(format t "~%~%>> favorable currents, sensors off: ~%")
	(energy-exp 0 0 1 1 0.3 0.3 nil)

	(format t "~%~%>> favorable currents, sensors on: ~%")
	(energy-exp 0 0 1 1 0.3 0.3 t)

	(format t "~%~%>> strongly favorable currents, sensors off: ~%")
	(energy-exp 0 0 1 1 1.1 1.1 nil)

	(format t "~%~%>> strongly favorable currents, sensors on: ~%")
	(energy-exp 0 0 1 1 1.1 1.1 t)

	(format t "~%~%>> unaligned favorable currents, sensors off: ~%")
	(energy-exp 0 0 1 1 0.4 0.2 nil)

	(format t "~%~%>> unaligned favorable currents, sensors on: ~%")
	(energy-exp 0 0 1 1 0.4 0.2 t)

	(format t "~%~%>> perpendicular currents, sensors off: ~%")
	(energy-exp 0 0 1 1 0.3 -0.3 nil)

	(format t "~%~%>> perpendicular currents, sensors on: ~%")
	(energy-exp 0 0 1 1 0.3 -0.3 t)

	(format t "~%~%>> adverse currents, sensors off: ~%")
	(energy-exp 0 0 1 1 -0.3 -0.3 nil)

	(format t "~%~%>> adverse currents, sensors on: ~%")
	(energy-exp 0 0 1 1 -0.3 -0.3 t)

	(format t "~%~%>> unaligned adverse currents, sensors off: ~%")
	(energy-exp 0 0 1 1 -0.34 -0.25 nil)

	(format t "~%~%>> unaligned adverse currents, sensors on: ~%")
	(energy-exp 0 0 1 1 -0.34 -0.25 t)

	(format t "~%~%>> strongly adverse currents, sensors off: ~%")
	(energy-exp 0 0 1 1 -1.5 -1.5 nil)

	(format t "~%~%>> strongly adverse currents, sensors on: ~%")
	(energy-exp 0 0 1 1 -1.5 -1.5 t)
	)
