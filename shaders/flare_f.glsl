//GLSL
#version 110
uniform sampler2D glareTex;

varying vec2 uv;

void main()
    {
    int uGhosts=8;
    float uGhostDispersal=0.3;
    float uHaloWidth=0.45;
    vec2 texcoord = -uv + vec2(1.0, 1.0);
    //vec2 texelSize = 1.0 / vec2(textureSize(glareTex, 0));
 
    // ghost vector to image centre:
    vec2 ghostVec = (vec2(0.5, 0.5) - texcoord) * uGhostDispersal;
   
    // sample ghosts:  
    vec4 result = vec4(0.0, 0.0, 0.0, 0.0);
    for (int i = 0; i < uGhosts; ++i)
        { 
        vec2 offset =texcoord + ghostVec * float(i); 
        float weight = length(vec2(0.5, 0.5) - offset) / length(vec2(0.5, 0.5));
        weight = pow(1.0 - weight, 10.0);  
        result += texture2D(glareTex, offset)* weight; 
        } 
    // sample halo:
    vec2 haloVec = normalize(ghostVec) * uHaloWidth;
    float weight = length(vec2(0.5) - fract(texcoord + haloVec)) / length(vec2(0.5));
    weight = pow(1.0 - weight, 5.0);
    result += texture2D(glareTex, texcoord + haloVec) * weight;    
        
    gl_FragColor = result;
   }