#ifndef INK6RSSV1_H
#define INK6RSSV1_H

#include<math.h>

#define	    M_PI                            3.14159265358979323846   // pi

#define     MOTOR_RANGE_LIMIT_MAX           45
#define     MOTOR_RANGE_LIMIT_MIN           -135

#define     MOTOR_RESET_ANGLE               30

#define     SJOINT_ANGLE_MAX                18

#define     LA                              30
#define     LB                              200

#define     R                               120
#define     r                               130

#define     THETA_A1                        20
#define     THETA_A2                        100
#define     THETA_A3                        140
#define     THETA_A4                        220
#define     THETA_A5                        260
#define     THETA_A6                        340

#define     THETA_C1                        45
#define     THETA_C2                        75
#define     THETA_C3                        165
#define     THETA_C4                        195
#define     THETA_C5                        285
#define     THETA_C6                        315

#define     X0                              0
#define     Y0                              0
#define     Z0                              168

#define     ERROR_TOR                       1

#define     cosd(x)                         cos( (M_PI*x)/180 )
#define     sind(x)                         sin( (M_PI*x)/180 )
#define     acosd(x)                        ( 180*acos(x)/M_PI )
#define     asind(x)                        ( 180*asin(x)/M_PI )
#define     atand(x)                        ( 180*atan(x)/M_PI )

#pragma once
extern "C" __declspec(dllexport)  void    rotx(double theta, double pMatrix[3][3]);
extern "C" __declspec(dllexport)  void    roty(double theta, double pMatrix[3][3]);
extern "C" __declspec(dllexport)  void    rotz(double theta, double pMatrix[3][3]);
extern "C" __declspec(dllexport)  void    TransM(double yaw, double pitch, double roll, double pMatrix[3][3]);
//__declspec(dllexport)  void    ParamCalculate(void);

extern "C" __declspec(dllexport) int     InK6RSS(double Px, double Py, double Pz, double yaw, double pitch, double roll, double ThetaMn[6]);


#endif // INK6RSSV1_H
