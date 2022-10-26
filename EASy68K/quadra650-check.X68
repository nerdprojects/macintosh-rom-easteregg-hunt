    ORG    $0
START:

    moveq   #2,d0
    lea static_values, a0
label1:
   
    lea (keymap).w, a1
    adda.w 2(a0),a1
    move.w (a0),d2
    btst d2,(a1)
    beq.s label1
    btst #5,(keymap+6).w
    beq.s label2
    tst.l (a0)+
    dbf d0,label1
    
    SIMHALT

label2:
    SIMHALT
    
static_values
    * quadra 650 values ("l" "f" "w")
    dc.b 0, 5, 0, 4, 0, 3, 0, 0, 0, 5, 0, 1
    * quadra 700 values ("s" "e" "t")
    *dc.b 0, 1, 0, 0, 0, 6, 0, 1, 0, 1, 0, 2
    
    ORG    $174
keymap
    * all key pressed
    *dc.b $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF
    * l + f + w + esc + enter pressed
    dc.b $08, $20, $00, $00, $30, $00, $20, $00, $00, $00, $00, $00
    * s + e + t + esc + enter pressed
    *dc.b $02, $40, $02, $00, $10, $00, $20, $00, $00, $00, $00, $00

    END    START

*~Font name~Courier New~
*~Font size~10~
*~Tab type~1~
*~Tab size~4~
