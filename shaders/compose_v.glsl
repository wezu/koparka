//GLSL
#version 110
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform float time;
uniform vec2 screen_size;

void main()
    {
    gl_Position = p3d_ModelViewProjectionMatrix * gl_Vertex; 
    gl_TexCoord[0] = gl_Position*0.5+0.5;
    //the noise texture is 512x512, we want to repeat it if the screen is bigger
    vec2 factor=screen_size/vec2(512.0, 512.0);
    gl_TexCoord[1] = ((gl_Position*0.5+0.5)*vec4(factor.xy, 1.0, 1.0))+vec4(0.0, time*0.2, 0.0, 0.0);
    }