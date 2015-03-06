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
    float sharpness=0.009;
    vec2 uv=gl_Position.xy*0.5+0.5;
    uv0= uv + vec2( -0.326212, -0.405805)*sharpness;
    uv1= uv + vec2(-0.840144, -0.073580)*sharpness;
    uv2= uv + vec2(-0.695914, 0.457137)*sharpness;
    uv3= uv + vec2(-0.203345, 0.620716)*sharpness;
    uv4= uv + vec2(0.962340, -0.194983)*sharpness;
    uv5= uv + vec2(0.473434, -0.480026)*sharpness;
    uv6= uv + vec2(0.519456, 0.767022)*sharpness;
    uv7= uv + vec2(0.185461, -0.893124)*sharpness;
    uv8= uv + vec2(0.507431, 0.064425)*sharpness;
    uv9= uv + vec2(0.896420, 0.412458)*sharpness;
    uv10= uv + vec2(-0.321940, -0.932615)*sharpness;
    uv11= uv + vec2(-0.791559, -0.597705)*sharpness;
    }