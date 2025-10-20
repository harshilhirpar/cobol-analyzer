      *> TODO - improve the explanation of this example
       IDENTIFICATION DIVISION.
       PROGRAM-ID. 08_REDEFINES.
       
       DATA DIVISION.
           WORKING-STORAGE SECTION.
           01 var-num1   PIC 9(10) VALUE zero.
           01 var-num2   PIC 9(10) VALUE zero.
           01 var-result-dec PIC z(9)9.99 VALUE zero.
           01 var-result REDEFINES var-result-dec PIC 9(12).
           01 var-remainder-dec PIC z(9)9.99 VALUE zero.
           01 var-remainder REDEFINES var-remainder-dec PIC 9(12).
           
      
       PROCEDURE DIVISION.
           DISPLAY "Enter number 1: ".
           ACCEPT var-num1.
           DISPLAY "Enter number 2: ".
           ACCEPT var-num2.

           DIVIDE var-num1 BY var-num2 GIVING var-result-dec
           REMAINDER var-remainder-dec.

           DISPLAY "Divide as decimals: ".
           DISPLAY "Result : "var-result-dec.
           DISPLAY "Reminder : "var-remainder-dec.
           DISPLAY spaces.


           DISPLAY "Divide as integers: ".
           DISPLAY "Result : "var-result.
           DISPLAY "Reminder : "var-remainder.
           DISPLAY spaces.

       STOP RUN.