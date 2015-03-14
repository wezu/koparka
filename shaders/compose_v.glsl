//GLSL
#version 110
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform float time;

void main()
    {
    gl_Position = p3d_ModelViewProjectionMatrix * gl_Vertex; 
    gl_TexCoord[0] = gl_Position*0.5+0.5;
    gl_TexCoord[1] = (gl_Position*0.5+0.5)-vec4(0.0, time*0.2, 0.0, 0.0);
    }