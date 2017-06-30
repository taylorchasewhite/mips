begin
   int i;
   i := 0;
   while (i < 5)
   {
      int j;
      j := 0;
      write("starting while loop ", i);
      while (j < 5)
      {
         j := j + 1;
         write(i, ", ", j);
      }
      i := i + 1;
      write("i is equal to ", i);
   }
end
