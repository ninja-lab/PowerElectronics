// Automatically generated C++ file on Thu Jul 11 17:01:43 2024
//
// To build with Digital Mars C++ Compiler:
//
//    dmc -mn -WD rpp_part1_x1.cpp kernel32.lib

#include <cmath>
extern "C" __declspec(dllexport) int (*Display)(const char *format, ...) = 0; // works like printf()
extern "C" __declspec(dllexport) const double *DegreesC                  = 0; // pointer to current circuit temperature
//double
//Ts,                     // switching period
//D,                      // duty cycle
//Sawtooth,               // sawtooth waveform
//PWM;                    // pwm output

union uData
{
   bool b;
   char c;
   unsigned char uc;
   short s;
   unsigned short us;
   int i;
   unsigned int ui;
   float f;
   double d;
   long long int i64;
   unsigned long long int ui64;
   char *str;
   unsigned char *bytes;
};

// int DllMain() must exist and return 1 for a process to load the .DLL
// See https://docs.microsoft.com/en-us/windows/win32/dlls/dllmain for more information.
int __stdcall DllMain(void *module, unsigned int reason, void *reserved) { return 1; }

// #undef pin names lest they collide with names in any header file(s) you might include.
#undef Sawtooth
#undef PWMH
#undef PWML

extern "C" __declspec(dllexport) void rpp_part1_x1(void **opaque, double t, union uData *data)
{

   double  frq      = data[0].d; // input
   double &Sawtooth = data[1].d; // output
   double  &PWMH      = data[2].d; // output
   double  &PWML      = data[3].d; // output
   double Ts;
   double D;

// Implement module evaluation code here:
      Ts= 1/frq; //200 kHz switching frequency
      D= 0.5;

      Sawtooth= t/Ts - floor(t/Ts); // sawtooth waveform generation

      if (D>Sawtooth) {PWMH= 5; PWML=0;}    // PWM signal generation
      else {PWMH= 0; PWML=5;}


}
