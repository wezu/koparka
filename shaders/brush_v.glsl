//GLSL
#version 110
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelMatrix;
attribute vec4 p3d_Vertex;
attribute vec4 p3d_Color;
attribute vec2 p3d_MultiTexCoord0;

varying vec4 color;
varying vec2 uv;
varying vec2 map_uv;

void main()
    {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;     
    color=p3d_Color;
    uv=p3d_MultiTexCoord0;
    vec4 w_pos=p3d_ModelMatrix * p3d_Vertex;   
    map_uv=w_pos.xy/512.0;
    }
