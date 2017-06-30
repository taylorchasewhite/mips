begin
   int i;
   i := 0;
   while (i < 5)
   {
      int j;
      j := 0;
      while (j < 5)
      {
         bool x;
         bool y;
         bool z;
         x := (i + j) % 3 == 0;
         y := i % 2 == 0;
         z := j % 2 == 0;
         if (x and (y or z))
         {
            write(i, " ", j, " \n");
         }
         j := j + 1;
      }
      i := i + 1;
   }
end
