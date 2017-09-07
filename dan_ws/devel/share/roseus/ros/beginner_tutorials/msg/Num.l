;; Auto-generated. Do not edit!


(when (boundp 'beginner_tutorials::Num)
  (if (not (find-package "BEGINNER_TUTORIALS"))
    (make-package "BEGINNER_TUTORIALS"))
  (shadow 'Num (find-package "BEGINNER_TUTORIALS")))
(unless (find-package "BEGINNER_TUTORIALS::NUM")
  (make-package "BEGINNER_TUTORIALS::NUM"))

(in-package "ROS")
;;//! \htmlinclude Num.msg.html


(defclass beginner_tutorials::Num
  :super ros::object
  :slots (_Amr ))

(defmethod beginner_tutorials::Num
  (:init
   (&key
    ((:Amr __Amr) "")
    )
   (send-super :init)
   (setq _Amr (string __Amr))
   self)
  (:Amr
   (&optional __Amr)
   (if __Amr (setq _Amr __Amr)) _Amr)
  (:serialization-length
   ()
   (+
    ;; string _Amr
    4 (length _Amr)
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; string _Amr
       (write-long (length _Amr) s) (princ _Amr s)
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; string _Amr
     (let (n) (setq n (sys::peek buf ptr- :integer)) (incf ptr- 4) (setq _Amr (subseq buf ptr- (+ ptr- n))) (incf ptr- n))
   ;;
   self)
  )

(setf (get beginner_tutorials::Num :md5sum-) "41627bb8959d7ae85c352700984f35cc")
(setf (get beginner_tutorials::Num :datatype-) "beginner_tutorials/Num")
(setf (get beginner_tutorials::Num :definition-)
      "string Amr

")



(provide :beginner_tutorials/Num "41627bb8959d7ae85c352700984f35cc")


