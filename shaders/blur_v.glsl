//GLSL
#version 110
uniform mat4 p3d_ModelViewProjectionMatrix;
varying vec2 uv0;
varying vec2 uv1;
varying vec2 uv2;
varying vec2 uv3;
varying vec2 uv4;
varying vec2 uv5;
varying vec2 uv6;
varying vec2 uv7;
varying vec2 uv8;
varying vec2 uv9;
varying vec2 uv10;
varying vec2 uv11;

void main()
    {
    gl_Position = p3d_ModelViewProjectionMatrix * gl_Vertex; 
    vec2 uv=gl_Position.xy*0.5+0.5;
    uv0 = uv+vec2(-0.00652424,-0.0081161);
    uv1 = uv+vec2(-0.01680288,-0.0014716);
    uv2 = uv+vec2(-0.01391828,0.00914274);
    uv3 = uv+vec2(-0.0040669,0.01241432);
    uv4 = uv+vec2(0.0192468,-0.00389966);
    uv5 = uv+vec2(0.00946868,-0.00960052);
    uv6 = uv+vec2(0.01038912,0.01534044);
    uv7 = uv+vec2(0.00370922,-0.01786248);
    uv8 = uv+vec2(0.01014862,0.0012885);
    uv9 = uv+vec2(0.0179284,0.00824916);
    uv10 = uv+vec2(-0.0064388,-0.0186523);
    uv11 = uv+vec2(-0.01583118,-0.0119541);
    }