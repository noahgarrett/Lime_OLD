; ModuleID = "main"
target triple = "x86_64-pc-windows-msvc"
target datalayout = ""

declare i32 @"printf"(i8* %".1", ...)

define i32 @"gimme_42"()
{
gimme_42_entry:
  ret i32 42
}

define i32 @"main"()
{
main_entry:
  %".2" = alloca i32
  store i32 5, i32* %".2"
  %".4" = alloca [7 x i8]
  store [7 x i8] c"apples\00", [7 x i8]* %".4"
  %".6" = load i32, i32* %".2"
  %".7" = alloca [9 x i8]
  store [9 x i8] c"yes %d\0a\00\00", [9 x i8]* %".7"
  %".9" = getelementptr [9 x i8], [9 x i8]* %".7", i32 0, i32 0
  %".10" = call i32 (i8*, ...) @"printf"(i8* %".9", i32 %".6")
  %".11" = call i32 @"gimme_42"()
  %".12" = alloca [15 x i8]
  store [15 x i8] c"imported: %d\0a\00\00", [15 x i8]* %".12"
  %".14" = getelementptr [15 x i8], [15 x i8]* %".12", i32 0, i32 0
  %".15" = call i32 (i8*, ...) @"printf"(i8* %".14", i32 %".11")
  ret i32 0
}
